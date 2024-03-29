# model settings
model = dict(
    type='Classification',
    pretrained=None,
    backbone=dict(
        type='ResNet_CIFAR',  # CIFAR version
        depth=18,
        num_stages=4,
        out_indices=(3,),  # no conv-1, x-1: stage-x
        style='pytorch'),
    head=dict(
        type='RegHead',
        loss=dict(type='RegressionLoss', mode="l1_loss", loss_weight=1.0),
        with_avg_pool=True, in_channels=512, out_channels=1)
)
