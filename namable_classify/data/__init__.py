# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/02data/init.ipynb.

# %% auto 0
__all__ = []

# %% ../../nbs/02data/init.ipynb 1
__all__ = None
del __all__

# %% ../../nbs/02data/init.ipynb 2
#| eval: false
import lazy_loader


__getattr__, __dir__, __all__ = lazy_loader.attach(
    __name__,
    submodules={
        'from_ssf',
        'infra',
        'transforms',
        'vtab_1k',
    },
    submod_attrs={
        'from_ssf': [
            'Cub2011',
            'DATA2CLS',
            'MultiEpochsDataLoader',
            'NABirds',
            'PrefetchLoader',
            'VtabDataset',
            'VtabSplit',
            'create_dataset',
            'create_loader',
            'create_transform',
            'cub2011',
            'dataset_factory',
            'dogs',
            'expand_to_chs',
            'fast_collate',
            'get_continuous_class_map',
            'has_inaturalist',
            'has_places365',
            'load_class_names',
            'load_hierarchy',
            'loader',
            'nabirds',
            'stanford_dogs',
            'transforms_direct_resize',
            'transforms_factory',
            'transforms_imagenet_eval',
            'transforms_imagenet_train',
            'transforms_simpleaug_train',
            'vtab',
        ],
        'infra': [
            'CIFAR100DataModule',
            'CIFAR10DataModule',
            'ClassificationDataConfig',
            'ClassificationDataModule',
            'FashionMNISTDataModule',
            'KMNISTTDataModule',
            'MNISTDataModule',
            'QMNISTDataModule',
            'TorchVisionDataModule',
            'auto_augment_choices',
            'cls_names_of',
            'dataloader_to_arrays',
            'dataset_name_choices',
            'simple_pixel_flatten_transform',
            'sksplit_for_torch',
        ],
        'transforms': [
            'CutoutPIL',
        ],
    },
)

__all__ = ['CIFAR100DataModule', 'CIFAR10DataModule',
           'ClassificationDataConfig', 'ClassificationDataModule', 'Cub2011',
           'CutoutPIL', 'DATA2CLS', 'FashionMNISTDataModule',
           'KMNISTTDataModule', 'MNISTDataModule', 'MultiEpochsDataLoader',
           'NABirds', 'PrefetchLoader', 'QMNISTDataModule',
           'TorchVisionDataModule', 'VtabDataset', 'VtabSplit',
           'auto_augment_choices', 'cls_names_of', 'create_dataset',
           'create_loader', 'create_transform', 'cub2011',
           'dataloader_to_arrays', 'dataset_factory', 'dataset_name_choices',
           'dogs', 'expand_to_chs', 'fast_collate', 'from_ssf',
           'get_continuous_class_map', 'has_inaturalist', 'has_places365',
           'infra', 'load_class_names', 'load_hierarchy', 'loader', 'nabirds',
           'simple_pixel_flatten_transform', 'sksplit_for_torch',
           'stanford_dogs', 'transforms', 'transforms_direct_resize',
           'transforms_factory', 'transforms_imagenet_eval',
           'transforms_imagenet_train', 'transforms_simpleaug_train', 'vtab',
           'vtab_1k']
