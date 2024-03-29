_base_ = [
    '../_base_/models/r50.py',
    '../_base_/datasets/stl10_sz96_4xbs64.py',
    '../_base_/default_runtime.py',
]

# model settings
model = dict(
    backbone=dict(frozen_stages=4),
    head=dict(num_classes=10))

# optimizer
optimizer = dict(type='SGD', lr=1.0, momentum=0.9, weight_decay=0.)

# learning policy
lr_config = dict(policy='step', step=[60, 80])

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=100)
