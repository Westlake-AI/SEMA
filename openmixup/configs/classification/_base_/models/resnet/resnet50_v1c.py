# model settings
model = dict(
    type='Classification',
    pretrained=None,
    backbone=dict(
        type='ResNetV1c',
        depth=50,
        num_stages=4,
        out_indices=(3,),  # x-1: stage-x
        style='pytorch'),
    head=dict(
        type='ClsHead',
        loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        with_avg_pool=True, in_channels=2048, num_classes=1000)
)
