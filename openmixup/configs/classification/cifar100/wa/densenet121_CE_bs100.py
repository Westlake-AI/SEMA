_base_ = [
    '../../_base_/datasets/cifar100/sz32_bs100.py',
    '../../_base_/default_runtime.py',
]

# model settings
model = dict(
    type='Classification',
    pretrained=None,
    backbone=dict(
        type='DenseNet_CIFAR', arch='121',
        out_indices=(3,),  # x-1: stage-x
    ),
    head=dict(
        type='ClsHead',  # normal CE loss
        loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        with_avg_pool=True, multi_label=False, in_channels=1024, num_classes=100)
)

# optimizer
optimizer = dict(type='SGD', lr=0.1, momentum=0.9, weight_decay=0.0001)

# fp16
use_fp16 = False
fp16 = dict(type='mmcv', loss_scale='dynamic')
optimizer_config = dict(update_interval=1, grad_clip=None)

# learning policy
lr_config = dict(policy='CosineAnnealing', min_lr=0.)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=200)
