"""automatically research on the relationship between the performance and meta parameters (a.k.a. hyperparameters or config) via searching (a.k.a. sweeping) experiments."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/04auto/exp_mutiple.ipynb.

# %% auto 0
__all__ = ['fixed_meta_parameters', 'study_results', 'backbone_name2pe', 'peft_to_try', 'delta_to_try', 'yuequ_to_try',
           'username', 'password', 'host', 'port', 'database_name', 'postgres_url', 'study', 'objective']

# %% ../../../nbs/04auto/exp_mutiple.ipynb 4
import os
os.environ['HF_ENDPOINT'] = "https://hf-mirror.com"

# %% ../../../nbs/04auto/exp_mutiple.ipynb 5
from ...nucleus import ClassificationTask, ClassificationTaskConfig
from boguan_yuequ.auto.nucleus import AutoYueQuAlgorithm
import lightning as L
from ...utils import runs_path
from lightning.pytorch.callbacks.early_stopping import EarlyStopping
from lightning.pytorch.callbacks import ModelSummary, StochasticWeightAveraging, DeviceStatsMonitor, LearningRateMonitor, LearningRateFinder, BatchSizeFinder
from lightning.pytorch.loggers import TensorBoardLogger, CSVLogger, WandbLogger

# %% ../../../nbs/04auto/exp_mutiple.ipynb 6
from ...nucleus import ClassificationModelConfig, ClassificationTaskConfig, ClassificationDataConfig
fixed_meta_parameters = ClassificationTaskConfig(
    experiment_project = "Homogeneous dwarf model is all you need for tuning pretrained giant model.", 
    # experiment_name = "Auto experiment", 
    experiment_task = "Auto experiment Stage 1 (single run, short epoches)", 
    label_smoothing=0.1,  # 未必固定。
    cls_model_config=ClassificationModelConfig(
        # checkpoint = "google/vit-base-patch16-224-in21k"
    ), 
    dataset_config = ClassificationDataConfig(
        # batch_size=64, # 经过前期经验, 这个方便站在61服务器跑, 大概10G显存。 固定基于这个调参
        batch_size=16,
    )
)


# %% ../../../nbs/04auto/exp_mutiple.ipynb 8
study_results = [] # 准备装入 dict

# %% ../../../nbs/04auto/exp_mutiple.ipynb 9
# 需要跑哪些backbone 和 对应的 pe呢？
from boguan_yuequ.benchmarking import pe_list_tiny_for_all_size, backbone_names
# from transformers import AutoModel
# # tiny+tiny vs tiny full vs tiny full_lora 也是有意义的对比，所以不做截断。
# for config, pe in zip(configs, pe_list_tiny_for_all_size):
#     model = AutoModel.from_pretrained(config)
#     yuequ = AutoYueQuAlgorithm(model, 'lora', pe)
#     model = yuequ.adapted_model
#     pe = yuequ.pe
backbone_name2pe = {backbone_name:pe for pe, backbone_name in zip(pe_list_tiny_for_all_size, backbone_names)}

# %% ../../../nbs/04auto/exp_mutiple.ipynb 11
# 需要跑哪些算法呢？
# from boguan_yuequ.auto import huggingface_peft_budget_config_key, thu_nlp_opendelta_budget_config_key
from boguan_yuequ.auto.integrations.peft import huggingface_peft_budget_config_key
from boguan_yuequ.auto.integrations.opendelta import thunlp_opendelta_budget_config_key

peft_to_try = [k.name for k in huggingface_peft_budget_config_key.keys()]
delta_to_try = [k for k in thunlp_opendelta_budget_config_key.keys() if k.upper() not in peft_to_try]
yuequ_to_try = peft_to_try + delta_to_try

# %% ../../../nbs/04auto/exp_mutiple.ipynb 15
# full_finetune 和 新方法单列
# 这里只跑baseline
from boguan_yuequ.benchmarking import pe_list_tiny_for_all_size, backbone_names
import optuna
from ...utils import logger
from rich.prompt import Prompt

import optuna.exceptions

def objective(trial, num_of_repeated_experiments = 5):
    # TODO 对每一个目标超参数 分开去做？ grid search
    # for yuequ in yuequ_tried_algs:
    
    meta_parameters = fixed_meta_parameters.copy()
    # 修改超参
    
    # 目标超参被建议
    meta_parameters.yuequ = trial.suggest_categorical("yuequ", yuequ_to_try)
    # choice = trial.suggest_categorical("pe_and_backbone_choice", list(range(len(backbone_names))))
    backbone_name = trial.suggest_categorical("backbone", backbone_names)
    meta_parameters.cls_model_config.checkpoint = backbone_name
    meta_parameters.yuequ_pe = backbone_name2pe[backbone_name]
    trial.set_user_attr("parameter_efficiency", meta_parameters.yuequ_pe) # 用于后续分析实验结果
    
    # 接下来是无关变量
# f"{yuequ}-learning_rate"

    # meta_parameters.learning_rate = trial.suggest_float(f"learning_rate", 1e-5, 1e-1, log=True)
    # meta_parameters.learning_rate = trial.suggest_float(f"learning_rate", 1e-5, 1e-2, log=True) # 正则化，建议的是Batch Size=64的学习率
    meta_parameters.learning_rate = trial.suggest_float(f"learning_rate", 1e-4, 4e-2, log=True) # 正则化，建议的是Batch Size=64的学习率
    
    result_dict = dict()

    metric_names = set()
    # 重复试验
    for experiment_index in range(num_of_repeated_experiments):
        meta_parameters.experiment_index = experiment_index
        # 当我们选定 experiment_index 之后，就不要随机建议参数了，现在我们元参数保持一样，重复5次随机实验。
        try:
            val_result, test_result = run_with_config(
                meta_parameters, trial, "val_acc1", "max"
            )
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error in experiment {experiment_index}, May be you can\n"
                         "1. Stop the optuna study and you debug and fix the buggy code. "
                         "2. Searched optuna trial is invalid as an input, so just prune this trial and continue. "
                         )
            choice = Prompt.ask("What should we do now?",
                                choices=["1", "2"], default="1")
            if choice == "1":
                raise e
            else:
                raise optuna.exceptions.TrialPruned()
            
        # 注意不要用 test_acc1 调参。
        # 我们的原则是每一个目标超参验证集到最优, 然后再用最优的超参得到的模型(其实应该重新训练一遍)在测试集上测试。
        # 在论文研究的第一阶段，应该调参。时间不够的话
        
        single_run_result = val_result[0] | test_result[0]
        metric_names.update(single_run_result.keys())
        single_run_result = {f"{k}-run{experiment_index}":v for k, v in single_run_result.items()}
        for k, v in single_run_result.items():
            trial.set_user_attr(k, v)
        result_dict|=single_run_result
        
        trial.report(single_run_result[f"val_acc1-run{experiment_index}"], experiment_index)
        # if trial.should_prune():
        #     # Return the current predicted value instead of raising `TrialPruned`.
        #     # This is a workaround to tell the Optuna about the evaluation
        #     # results in pruned trials.
        #     for metric_name in metric_names:
        #         all_runs_results = [result_dict[f"{metric_name}-run{i}"] for i in range(num_of_repeated_experiments)]
        #         result_dict[f"{metric_name}-mean"] = sum(all_runs_results) / len(all_runs_results)
        #         trial.set_user_attr(f"{metric_name}-mean", result_dict[f"{metric_name}-mean"])
        #     trial.set_user_attr(f"num_of_repeated", experiment_index+1)
        #     return result_dict["val_acc1-mean"]
    # 计算一下平均数
    for metric_name in metric_names:
        all_runs_results = [result_dict[f"{metric_name}-run{i}"] for i in range(num_of_repeated_experiments)]
        result_dict[f"{metric_name}-mean"] = sum(all_runs_results) / len(all_runs_results)
        trial.set_user_attr(f"{metric_name}-mean", result_dict[f"{metric_name}-mean"])
    trial.set_user_attr(f"num_of_repeated", num_of_repeated_experiments)
    return result_dict["val_acc1-mean"]
    

# %% ../../../nbs/04auto/exp_mutiple.ipynb 19
from ...utils import runs_path
from optuna.samplers import *
from optuna.pruners import *
# study_path = auto_exp_runs_path / "optuna_studies.db"
# sqlite_url = f"sqlite:///{study_path}"
# sqlite_url = f"sqlite://{study_path}"
# TODO 

username = 'ycm'
password = 'password'
# host = 'localhost'
host = '10.103.10.53'
port = 5432
database_name = 'namable_classify'
postgres_url = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}'
# pip install psycopg2-binary 
# postgres_url = 'postgresql://myuser:mypassword@localhost/mydatabase'
# TODO safety and privacy
study = optuna.create_study(
    # study_name="peft baselines benchmark",  # old version
    # study_name="peft baselines benchmark 11.3", 
    study_name="peft baselines benchmark 11.7", 
    # storage=sqlite_url, 
    storage=postgres_url, 
    load_if_exists=True, 
    direction="maximize", 
    # https://pub.aimind.so/a-deep-dive-in-optunas-advance-features-2e495e71435c
    # sampler=GPSampler(seed=42), 
    # sampler=TPESampler(seed=42), 
    # sampler=TPESampler(), 
    # https://github.com/optuna/optuna/issues/1647
    sampler=CmaEsSampler(consider_pruned_trials = True), 
    pruner=HyperbandPruner()
    # pruner=WilcoxonPruner()
    # CmaEsSampler(seed=42),  我们实验数量应该小于1000
    # WilcoxonPruner(min_n_trials=10) # 不适合这个，这个 immediate 是fold的情况
)
study.set_user_attr("contributors", ["Ye Canming"])
study.set_user_attr("fixed_meta_parameters", fixed_meta_parameters.json())
# 晚点再看
# https://optuna-integration.readthedocs.io/en/stable/reference/generated/optuna_integration.MLflowCallback.html

# %% ../../../nbs/04auto/exp_mutiple.ipynb 20
# study.optimize(objective, n_trials=100)
study.optimize(lambda trial: objective(trial, num_of_repeated_experiments=1), 
               n_trials=100)