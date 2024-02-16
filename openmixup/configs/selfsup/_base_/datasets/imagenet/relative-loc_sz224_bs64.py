# dataset settings
data_source_cfg = dict(type='ImageNet', return_label=False)
# ImageNet dataset
data_train_list = 'data/meta/ImageNet/train_full.txt'
data_train_root = 'data/ImageNet/train'
data_test_list = 'data/meta/ImageNet/val.txt'
data_test_root = 'data/ImageNet/val/'

dataset_type = 'RelativeLocDataset'
img_norm_cfg = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
train_pipeline = [
    dict(type='Resize', size=292),
    dict(type='RandomCrop', size=255),
    dict(type='RandomGrayscale', p=0.66),
]
test_pipeline = [
    dict(type='Resize', size=292),
    dict(type='CenterCrop', size=255),
]
format_pipeline = [
    dict(type='ToTensor'),
    dict(type='Normalize', **img_norm_cfg),
]

# prefetch
prefetch = False

# dataset summary
data = dict(
    imgs_per_gpu=64,  # V100: 64 x 8gpus = bs512
    workers_per_gpu=6,  # according to total cpus cores, usually 4 workers per 32~128 imgs
    train=dict(
        type=dataset_type,
        data_source=dict(
            list_file=data_train_list, root=data_train_root,
            **data_source_cfg),
        pipeline=train_pipeline,
        format_pipeline=format_pipeline,
        prefetch=prefetch),
    val=dict(
        type=dataset_type,
        data_source=dict(
            list_file=data_test_list, root=data_test_root,
            **data_source_cfg),
        pipeline=test_pipeline,
        format_pipeline=format_pipeline,
        prefetch=prefetch),
)

# checkpoint
checkpoint_config = dict(interval=10, max_keep_ckpts=1)
