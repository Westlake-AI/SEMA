_base_ = [
    '../../_base_/models/efficientnet_v2/efficientnet_v2_m.py',
    '../../_base_/datasets/imagenet/basic_sz224_4xbs64.py',
    '../../_base_/default_runtime.py',
]

# data
img_norm_cfg = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
train_pipeline = [
    dict(type='RandomResizedCropForEfficient',
        size=384,
        efficientnet_style=True,
        interpolation='bicubic'),  # bicubic
    dict(type='RandomHorizontalFlip'),
]
test_pipeline = [
    dict(type='CenterCropForEfficientNet',
        size=480,
        efficientnet_style=True,
        interpolation='bicubic'),  # bicubic
    dict(type='ToTensor'),
    dict(type='Normalize', **img_norm_cfg),
]
# prefetch
prefetch = False
if not prefetch:
    train_pipeline.extend([dict(type='ToTensor'), dict(type='Normalize', **img_norm_cfg)])

data = dict(
    imgs_per_gpu=32,
    workers_per_gpu=8,
    train=dict(
        pipeline=train_pipeline,
        prefetch=prefetch,
    ),
    val=dict(
        pipeline=test_pipeline,
        prefetch=False,
    ))

# optimizer
optimizer = dict(type='SGD', lr=0.1, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)

# lr scheduler
lr_config = dict(
    policy='CosineAnnealing',
    by_epoch=False, min_lr=1e-6)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=100)
