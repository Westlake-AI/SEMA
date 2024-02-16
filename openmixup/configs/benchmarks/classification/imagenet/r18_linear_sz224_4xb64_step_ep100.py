_base_ = [
    '../_base_/models/r18.py',
    '../_base_/datasets/imagenet_sz224_4xbs64.py',
    '../_base_/default_runtime.py',
]

# model settings
model = dict(
    backbone=dict(frozen_stages=4),
    head=dict(num_classes=1000))

# optimizer
optimizer = dict(type='SGD', lr=30., momentum=0.9, weight_decay=0.)

# learning policy
lr_config = dict(policy='step', step=[60, 80])

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=100)
