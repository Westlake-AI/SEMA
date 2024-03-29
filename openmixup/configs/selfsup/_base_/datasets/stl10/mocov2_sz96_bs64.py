# dataset settings
data_source_cfg = dict(type='ImageNet', return_label=False)
# ImageNet dataset
data_train_list = 'data/meta/STL10/train_10w_unlabeled.txt'
data_train_root = 'data/stl10/train/'
data_test_list = 'data/meta/STL10/test_8k_unlabeled.txt'
data_test_root = 'data/stl10/test/'

dataset_type = 'MultiViewDataset'
img_norm_cfg = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
train_pipeline = [
    dict(type='RandomResizedCrop', size=96, scale=(0.2, 1.)),
    dict(type='RandomHorizontalFlip'),
    dict(type='RandomAppliedTrans',
        transforms=[dict(
            type='ColorJitter',
            brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1)
        ],
        p=0.8),
    dict(type='RandomGrayscale', p=0.2),
    dict(type='GaussianBlur', sigma_min=0.1, sigma_max=2.0, p=0.5),
]

# prefetch
prefetch = True
if not prefetch:
    train_pipeline.extend([dict(type='ToTensor'), dict(type='Normalize', **img_norm_cfg)])

# dataset summary
data = dict(
    imgs_per_gpu=64,
    workers_per_gpu=4,
    drop_last=True,
    train=dict(
        type=dataset_type,
        data_source=dict(
            list_file=data_train_list, root=data_train_root,
            **data_source_cfg),
        num_views=[2],
        pipelines=[train_pipeline],
        prefetch=prefetch,
    ))

# checkpoint
checkpoint_config = dict(interval=10, max_keep_ckpts=1)
