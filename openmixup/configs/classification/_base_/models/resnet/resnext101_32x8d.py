# model settings
model = dict(
    type='Classification',
    pretrained=None,
    backbone=dict(
        type='ResNeXt',
        depth=101,
        groups=32, width_per_group=8,  # 32x8d
        num_stages=4,
        out_indices=(3,),  # x-1: stage-x
        style='pytorch'),
    head=dict(
        type='ClsHead',
        loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        with_avg_pool=True, in_channels=2048, num_classes=1000)
)
