# model settings
model = dict(
    type='Classification',
    pretrained=None,
    backbone=dict(
        type='DenseNet', arch='161',
        out_indices=(3,),  # x-1: stage-x
    ),
    head=dict(
        type='ClsHead',
        loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        with_avg_pool=True, in_channels=2208, num_classes=1000)
)
