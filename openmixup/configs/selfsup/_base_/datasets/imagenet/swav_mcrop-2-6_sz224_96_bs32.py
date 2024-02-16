# dataset settings
data_source_cfg = dict(type='ImageNet', return_label=False)
# ImageNet dataset
data_train_list = 'data/meta/ImageNet/train_full.txt'
data_train_root = 'data/ImageNet/train'
data_test_list = 'data/meta/ImageNet/val.txt'
data_test_root = 'data/ImageNet/val/'

dataset_type = 'MultiViewDataset'
img_norm_cfg = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
num_crops = [2, 6]
color_distort_strength = 1.0
train_pipeline1 = [
    dict(type='RandomResizedCrop', size=224, scale=(0.14, 1.), interpolation=3),
    dict(type='RandomHorizontalFlip'),
    dict(type='RandomAppliedTrans',
        transforms=[dict(
            type='ColorJitter',
            brightness=0.8 * color_distort_strength,
            contrast=0.8 * color_distort_strength,
            saturation=0.8 * color_distort_strength,
            hue=0.2 * color_distort_strength)
        ],
        p=0.8),
    dict(type='RandomGrayscale', p=0.2),
    dict(type='GaussianBlur', sigma_min=0.1, sigma_max=2.0, p=0.5),
]
train_pipeline2 = [
    dict(type='RandomResizedCrop', size=96, scale=(0.05, 0.14)),
    dict(type='RandomHorizontalFlip'),
    dict(type='RandomAppliedTrans',
        transforms=[dict(
            type='ColorJitter',
            brightness=0.8 * color_distort_strength,
            contrast=0.8 * color_distort_strength,
            saturation=0.8 * color_distort_strength,
            hue=0.2 * color_distort_strength)
        ],
        p=0.8),
    dict(type='RandomGrayscale', p=0.2),
    dict(type='GaussianBlur', sigma_min=0.1, sigma_max=2.0, p=0.5),
]

# prefetch
prefetch = True
if not prefetch:
    train_pipeline1.extend([dict(type='ToTensor'), dict(type='Normalize', **img_norm_cfg)])
    train_pipeline2.extend([dict(type='ToTensor'), dict(type='Normalize', **img_norm_cfg)])

# dataset summary
data = dict(
    imgs_per_gpu=64,  # V100: 64 x 8gpus x 8 accumulates = bs4096
    workers_per_gpu=6,  # according to total cpus cores, usually 4 workers per 32~128 imgs
    train=dict(
        type=dataset_type,
        data_source=dict(
            list_file=data_train_list, root=data_train_root,
            **data_source_cfg),
        num_views=num_crops,
        pipelines=[train_pipeline1, train_pipeline2],
        prefetch=prefetch,
    ))

# checkpoint
checkpoint_config = dict(interval=10, max_keep_ckpts=1)
