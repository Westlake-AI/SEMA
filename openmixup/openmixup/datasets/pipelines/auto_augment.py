# Copyright (c) OpenMMLab. All rights reserved.
# refer to mmclassification: https://github.com/open-mmlab/mmclassification/tree/master/mmcls/datasets/pipelines/auto_augment.py
import copy
import inspect
import random
from numbers import Number
from typing import List, Optional, Sequence, Tuple, Union
from PIL import Image
from timm.data import create_transform
import cv2
import mmcv
import numpy as np

from ..registry import PIPELINES
from .compose import BuildCompose
# from torchvision.transforms import Compose

# Default hyperparameters for all Ops
_HPARAMS_DEFAULT = dict(pad_val=128)
# timm data constants
DEFAULT_CROP_PCT = 0.875
IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)
IMAGENET_INCEPTION_MEAN = (0.5, 0.5, 0.5)
IMAGENET_INCEPTION_STD = (0.5, 0.5, 0.5)
IMAGENET_DPN_MEAN = (124 / 255, 117 / 255, 104 / 255)
IMAGENET_DPN_STD = tuple([1 / (.0167 * 255)] * 3)


def random_negative(value, random_negative_prob):
    """Randomly negate value based on random_negative_prob."""
    return -value if np.random.rand() < random_negative_prob else value


def merge_hparams(policy: dict, hparams: dict):
    """Merge hyperparameters into policy config.

    Only merge partial hyperparameters required of the policy.

    Args:
        policy (dict): Original policy config dict.
        hparams (dict): Hyperparameters need to be merged.

    Returns:
        dict: Policy config dict after adding ``hparams``.
    """
    op = PIPELINES.get(policy['type'])
    assert op is not None, f'Invalid policy type "{policy["type"]}".'
    for key, value in hparams.items():
        if policy.get(key, None) is not None:
            continue
        if key in inspect.getfullargspec(op.__init__).args:
            policy[key] = value
    return policy


@PIPELINES.register_module()
class AutoAugment(object):
    """Auto augmentation.

    This data augmentation is proposed in `AutoAugment: Learning Augmentation
    Policies from Data <https://arxiv.org/abs/1805.09501>`_.

    Args:
        policies (str | list[list[dict]]): The policies of auto augmentation.
            If string, use preset policies collection like "imagenet". If list,
            Each item is a sub policies, composed by several augmentation
            policy dicts. When AutoAugment is called, a random sub policies in
            ``policies`` will be selected to augment images.
        hparams (dict): Configs of hyperparameters. Hyperparameters will be
            used in policies that require these arguments if these arguments
            are not set in policy dicts. Defaults to use _HPARAMS_DEFAULT.
    """

    def __init__(self,
                 policies: Union[str, List[List[dict]]],
                 hparams: dict = _HPARAMS_DEFAULT):
        if isinstance(policies, str):
            assert policies in AUTOAUG_POLICIES, 'Invalid policies, ' \
                f'please choose from {list(AUTOAUG_POLICIES.keys())}.'
            policies = AUTOAUG_POLICIES[policies]
        assert isinstance(policies, list) and len(policies) > 0, \
            'Policies must be a non-empty list.'
        for policy in policies:
            assert isinstance(policy, list) and len(policy) > 0, \
                'Each policy in policies must be a non-empty list.'
            for augment in policy:
                assert isinstance(augment, dict) and 'type' in augment, \
                    'Each specific augmentation must be a dict with key' \
                    ' "type".'

        self.hparams = hparams
        policies = copy.deepcopy(policies)
        self.policies = []
        for sub in policies:
            merged_sub = [merge_hparams(policy, hparams) for policy in sub]
            self.policies.append(merged_sub)

        self.sub_policy = [BuildCompose(policy) for policy in self.policies]

    def __call__(self, img):
        sub_policy = random.choice(self.sub_policy)
        img = sub_policy(np.array(img))
        return Image.fromarray(img.astype(np.uint8))

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(policies={self.policies})'
        return repr_str


@PIPELINES.register_module()
class RandAugment(object):
    r"""Random augmentation.

    This data augmentation is proposed in `RandAugment: Practical automated
    data augmentation with a reduced search space
    <https://arxiv.org/abs/1909.13719>`_.

    Args:
        policies (list[dict]): The policies of random augmentation. Each
            policy in ``policies`` is one specific augmentation policy (dict).
            The policy shall at least have key `type`, indicating the type of
            augmentation. For those which have magnitude, (given to the fact
            they are named differently in different augmentation, )
            `magnitude_key` and `magnitude_range` shall be the magnitude
            argument (str) and the range of magnitude (tuple in the format of
            (val1, val2)), respectively. Note that val1 is not necessarily
            less than val2.
        num_policies (int): Number of policies to select from policies each
            time.
        magnitude_level (int | float): Magnitude level for all the augmentation
            selected.
        total_level (int | float): Total level for the magnitude. Defaults to
            30.
        magnitude_std (Number | str): Deviation of magnitude noise applied.

            - If positive number, magnitude is sampled from normal distribution
              (mean=magnitude, std=magnitude_std).
            - If 0 or negative number, magnitude remains unchanged.
            - If str "inf", magnitude is sampled from uniform distribution
              (range=[min, magnitude]).
        hparams (dict): Configs of hyperparameters. Hyperparameters will be
            used in policies that require these arguments if these arguments
            are not set in policy dicts. Defaults to use _HPARAMS_DEFAULT.

    Note:
        `magnitude_std` will introduce some randomness to policy, modified by
        https://github.com/rwightman/pytorch-image-models.

        When magnitude_std=0, we calculate the magnitude as follows:

        .. math::
            \text{magnitude} = \frac{\text{magnitude\_level}}
            {\text{total\_level}} \times (\text{val2} - \text{val1})
            + \text{val1}
    """

    def __init__(self,
                 policies: Union[str, List[dict]],
                 num_policies: int,
                 magnitude_level: int,
                 magnitude_std: Union[Number, str] = 0.,
                 total_level: int = 30,
                 use_numpy: bool = False,
                 hparams: dict = _HPARAMS_DEFAULT):
        if isinstance(policies, str):
            assert policies in RANDAUG_POLICIES, 'Invalid policies, ' \
                f'please choose from {list(RANDAUG_POLICIES.keys())}.'
            policies = RANDAUG_POLICIES[policies]
        assert isinstance(policies, list) and len(policies) > 0, \
            'Policies must be a non-empty list.'
        assert isinstance(num_policies, int), 'Number of policies must be ' \
            f'of int type, got {type(num_policies)} instead.'
        assert isinstance(magnitude_level, (int, float)), \
            'Magnitude level must be of int or float type, ' \
            f'got {type(magnitude_level)} instead.'
        assert isinstance(total_level, (int, float)),  'Total level must be ' \
            f'of int or float type, got {type(total_level)} instead.'

        assert isinstance(magnitude_std, (Number, str)), \
            'Magnitude std must be of number or str type, ' \
            f'got {type(magnitude_std)} instead.'
        if isinstance(magnitude_std, str):
            assert magnitude_std == 'inf', \
                'Magnitude std must be of number or "inf", ' \
                f'got "{magnitude_std}" instead.'

        assert num_policies > 0, 'num_policies must be greater than 0.'
        assert magnitude_level >= 0, 'magnitude_level must be no less than 0.'
        assert total_level > 0, 'total_level must be greater than 0.'

        self.num_policies = num_policies
        self.magnitude_level = magnitude_level
        self.magnitude_std = magnitude_std
        self.total_level = total_level
        self.hparams = hparams
        self.use_numpy = use_numpy
        policies = copy.deepcopy(policies)
        self._check_policies(policies)
        self.policies = [merge_hparams(policy, hparams) for policy in policies]

    def _check_policies(self, policies):
        for policy in policies:
            assert isinstance(policy, dict) and 'type' in policy, \
                'Each policy must be a dict with key "type".'
            type_name = policy['type']

            magnitude_key = policy.get('magnitude_key', None)
            if magnitude_key is not None:
                assert 'magnitude_range' in policy, \
                    f'RandAugment policy {type_name} needs `magnitude_range`.'
                magnitude_range = policy['magnitude_range']
                assert (isinstance(magnitude_range, Sequence)
                        and len(magnitude_range) == 2), \
                    f'`magnitude_range` of RandAugment policy {type_name} ' \
                    f'should be a Sequence with two numbers.'

    def _process_policies(self, policies):
        processed_policies = []
        for policy in policies:
            processed_policy = copy.deepcopy(policy)
            magnitude_key = processed_policy.pop('magnitude_key', None)
            if magnitude_key is not None:
                magnitude = self.magnitude_level
                # if magnitude_std is positive number or 'inf', move
                # magnitude_value randomly.
                if self.magnitude_std == 'inf':
                    magnitude = random.uniform(0, magnitude)
                elif self.magnitude_std > 0:
                    magnitude = random.gauss(magnitude, self.magnitude_std)
                    magnitude = min(self.total_level, max(0, magnitude))

                val1, val2 = processed_policy.pop('magnitude_range')
                magnitude = (magnitude / self.total_level) * (val2 -
                                                              val1) + val1

                processed_policy.update({magnitude_key: magnitude})
            processed_policies.append(processed_policy)
        return processed_policies

    def __call__(self, img):
        if self.num_policies == 0:
            return img
        sub_policy = random.choices(self.policies, k=self.num_policies)
        sub_policy = self._process_policies(sub_policy)
        sub_policy = BuildCompose(sub_policy)
        if self.use_numpy:
            img = sub_policy(img)
            return img
        else:
            img = sub_policy(np.array(img))
            return Image.fromarray(img.astype(np.uint8))

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(policies={self.policies}, '
        repr_str += f'num_policies={self.num_policies}, '
        repr_str += f'magnitude_level={self.magnitude_level}, '
        repr_str += f'total_level={self.total_level})'
        return repr_str


@PIPELINES.register_module()
class RandAugment_timm(object):
    """RandAugment data augmentation method based on
    `"RandAugment: Practical automated data augmentation
    with a reduced search space"
    <https://arxiv.org/abs/1909.13719>`_.

    This code is borrowed from <https://github.com/pengzhiliang/MAE-pytorch>
    """

    def __init__(self,
                 input_size=None,
                 color_jitter=None,
                 auto_augment=None,
                 interpolation=None,
                 re_prob=None,
                 re_mode=None,
                 re_count=None,
                 mean=None,
                 std=None):

        self.trans = create_transform(
            input_size=input_size,
            is_training=True,
            color_jitter=color_jitter,
            auto_augment=auto_augment,
            interpolation=interpolation,
            re_prob=re_prob,
            re_mode=re_mode,
            re_count=re_count,
            mean=mean,
            std=std,
        )

    def __call__(self, img):
        return self.trans(img)

    def __repr__(self) -> str:
        repr_str = self.__class__.__name__
        return repr_str


@PIPELINES.register_module()
class Shear(object):
    """Shear images.

    Args:
        magnitude (int | float): The magnitude used for shear.
        pad_val (int, Sequence[int]): Pixel pad_val value for constant fill.
            If a sequence of length 3, it is used to pad_val R, G, B channels
            respectively. Defaults to 128.
        prob (float): The probability for performing Shear therefore should be
            in range [0, 1]. Defaults to 0.5.
        direction (str): The shearing direction. Options are 'horizontal' and
            'vertical'. Defaults to 'horizontal'.
        random_negative_prob (float): The probability that turns the magnitude
            negative, which should be in range [0,1]. Defaults to 0.5.
        interpolation (str): Interpolation method. Options are 'nearest',
            'bilinear', 'bicubic', 'area', 'lanczos'. Defaults to 'bicubic'.
    """

    def __init__(self,
                 magnitude,
                 pad_val=128,
                 prob=0.5,
                 direction='horizontal',
                 random_negative_prob=0.5,
                 interpolation='bicubic'):
        assert isinstance(magnitude, (int, float)), 'The magnitude type must '\
            f'be int or float, but got {type(magnitude)} instead.'
        if isinstance(pad_val, int):
            pad_val = tuple([pad_val] * 3)
        elif isinstance(pad_val, Sequence):
            assert len(pad_val) == 3, 'pad_val as a tuple must have 3 ' \
                f'elements, got {len(pad_val)} instead.'
            assert all(isinstance(i, int) for i in pad_val), 'pad_val as a '\
                'tuple must got elements of int type.'
        else:
            raise TypeError('pad_val must be int or tuple with 3 elements.')
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert direction in ('horizontal', 'vertical'), 'direction must be ' \
            f'either "horizontal" or "vertical", got {direction} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.magnitude = magnitude
        self.pad_val = tuple(pad_val)
        self.prob = prob
        self.direction = direction
        self.random_negative_prob = random_negative_prob
        self.interpolation = interpolation

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        magnitude = random_negative(self.magnitude, self.random_negative_prob)
        img_sheared = mmcv.imshear(
            img,
            magnitude,
            direction=self.direction,
            border_value=self.pad_val,
            interpolation=self.interpolation)
        return img_sheared.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'pad_val={self.pad_val}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'direction={self.direction}, '
        repr_str += f'random_negative_prob={self.random_negative_prob}, '
        repr_str += f'interpolation={self.interpolation})'
        return repr_str


@PIPELINES.register_module()
class Translate(object):
    """Translate images.

    Args:
        magnitude (int | float): The magnitude used for translate. Note that
            the offset is calculated by magnitude * size in the corresponding
            direction. With a magnitude of 1, the whole image will be moved out
            of the range.
        pad_val (int, Sequence[int]): Pixel pad_val value for constant fill.
            If a sequence of length 3, it is used to pad_val R, G, B channels
            respectively. Defaults to 128.
        prob (float): The probability for performing translate therefore should
             be in range [0, 1]. Defaults to 0.5.
        direction (str): The translating direction. Options are 'horizontal'
            and 'vertical'. Defaults to 'horizontal'.
        random_negative_prob (float): The probability that turns the magnitude
            negative, which should be in range [0,1]. Defaults to 0.5.
        interpolation (str): Interpolation method. Options are 'nearest',
            'bilinear', 'bicubic', 'area', 'lanczos'. Defaults to 'nearest'.
    """

    def __init__(self,
                 magnitude,
                 pad_val=128,
                 prob=0.5,
                 direction='horizontal',
                 random_negative_prob=0.5,
                 interpolation='nearest'):
        assert isinstance(magnitude, (int, float)), 'The magnitude type must '\
            f'be int or float, but got {type(magnitude)} instead.'
        if isinstance(pad_val, int):
            pad_val = tuple([pad_val] * 3)
        elif isinstance(pad_val, Sequence):
            assert len(pad_val) == 3, 'pad_val as a tuple must have 3 ' \
                f'elements, got {len(pad_val)} instead.'
            assert all(isinstance(i, int) for i in pad_val), 'pad_val as a '\
                'tuple must got elements of int type.'
        else:
            raise TypeError('pad_val must be int or tuple with 3 elements.')
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert direction in ('horizontal', 'vertical'), 'direction must be ' \
            f'either "horizontal" or "vertical", got {direction} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.magnitude = magnitude
        self.pad_val = tuple(pad_val)
        self.prob = prob
        self.direction = direction
        self.random_negative_prob = random_negative_prob
        self.interpolation = interpolation

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        magnitude = random_negative(self.magnitude, self.random_negative_prob)
        height, width = img.shape[:2]
        if self.direction == 'horizontal':
            offset = magnitude * width
        else:
            offset = magnitude * height
        img_translated = mmcv.imtranslate(
            img,
            offset,
            direction=self.direction,
            border_value=self.pad_val,
            interpolation=self.interpolation)
        return img_translated.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'pad_val={self.pad_val}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'direction={self.direction}, '
        repr_str += f'random_negative_prob={self.random_negative_prob}, '
        repr_str += f'interpolation={self.interpolation})'
        return repr_str


@PIPELINES.register_module()
class Rotate(object):
    """Rotate images.

    Args:
        angle (float): The angle used for rotate. Positive values stand for
            clockwise rotation.
        center (tuple[float], optional): Center point (w, h) of the rotation in
            the source image. If None, the center of the image will be used.
            Defaults to None.
        scale (float): Isotropic scale factor. Defaults to 1.0.
        pad_val (int, Sequence[int]): Pixel pad_val value for constant fill.
            If a sequence of length 3, it is used to pad_val R, G, B channels
            respectively. Defaults to 128.
        prob (float): The probability for performing Rotate therefore should be
            in range [0, 1]. Defaults to 0.5.
        random_negative_prob (float): The probability that turns the angle
            negative, which should be in range [0,1]. Defaults to 0.5.
        interpolation (str): Interpolation method. Options are 'nearest',
            'bilinear', 'bicubic', 'area', 'lanczos'. Defaults to 'nearest'.
    """

    def __init__(self,
                 angle,
                 center=None,
                 scale=1.0,
                 pad_val=128,
                 prob=0.5,
                 random_negative_prob=0.5,
                 interpolation='nearest'):
        assert isinstance(angle, float), 'The angle type must be float, but ' \
            f'got {type(angle)} instead.'
        if isinstance(center, tuple):
            assert len(center) == 2, 'center as a tuple must have 2 ' \
                f'elements, got {len(center)} elements instead.'
        else:
            assert center is None, 'The center type' \
                f'must be tuple or None, got {type(center)} instead.'
        assert isinstance(scale, float), 'the scale type must be float, but ' \
            f'got {type(scale)} instead.'
        if isinstance(pad_val, int):
            pad_val = tuple([pad_val] * 3)
        elif isinstance(pad_val, Sequence):
            assert len(pad_val) == 3, 'pad_val as a tuple must have 3 ' \
                f'elements, got {len(pad_val)} instead.'
            assert all(isinstance(i, int) for i in pad_val), 'pad_val as a '\
                'tuple must got elements of int type.'
        else:
            raise TypeError('pad_val must be int or tuple with 3 elements.')
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.angle = angle
        self.center = center
        self.scale = scale
        self.pad_val = tuple(pad_val)
        self.prob = prob
        self.random_negative_prob = random_negative_prob
        self.interpolation = interpolation

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        angle = random_negative(self.angle, self.random_negative_prob)
        img_rotated = mmcv.imrotate(
            img,
            angle,
            center=self.center,
            scale=self.scale,
            border_value=self.pad_val,
            interpolation=self.interpolation)
        return img_rotated.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(angle={self.angle}, '
        repr_str += f'center={self.center}, '
        repr_str += f'scale={self.scale}, '
        repr_str += f'pad_val={self.pad_val}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'random_negative_prob={self.random_negative_prob}, '
        repr_str += f'interpolation={self.interpolation})'
        return repr_str


def auto_contrast(img, cutoff=0):
    """Auto adjust image contrast.
    This function maximize (normalize) image contrast by first removing cutoff
    percent of the lightest and darkest pixels from the histogram and remapping
    the image so that the darkest pixel becomes black (0), and the lightest
    becomes white (255).
    Args:
        img (ndarray): Image to be contrasted. BGR order.
        cutoff (int | float | tuple): The cutoff percent of the lightest and
            darkest pixels to be removed. If given as tuple, it shall be
            (low, high). Otherwise, the single value will be used for both.
            Defaults to 0.
    Returns:
        ndarray: The contrasted image.
    """

    def _auto_contrast_channel(im, c, cutoff):
        im = im[:, :, c]
        # Compute the histogram of the image channel.
        histo = np.histogram(im, 256, (0, 255))[0]
        # Remove cut-off percent pixels from histo
        histo_sum = np.cumsum(histo)
        cut_low = histo_sum[-1] * cutoff[0] // 100
        cut_high = histo_sum[-1] - histo_sum[-1] * cutoff[1] // 100
        histo_sum = np.clip(histo_sum, cut_low, cut_high) - cut_low
        histo = np.concatenate([[histo_sum[0]], np.diff(histo_sum)], 0)

        # Compute mapping
        low, high = np.nonzero(histo)[0][0], np.nonzero(histo)[0][-1]
        # If all the values have been cut off, return the origin img
        if low >= high:
            return im
        scale = 255.0 / (high - low)
        offset = -low * scale
        lut = np.array(range(256))
        lut = lut * scale + offset
        lut = np.clip(lut, 0, 255)
        return lut[im]

    if isinstance(cutoff, (int, float)):
        cutoff = (cutoff, cutoff)
    else:
        assert isinstance(cutoff, tuple), 'cutoff must be of type int, ' \
            f'float or tuple, but got {type(cutoff)} instead.'
    # Auto adjusts contrast for each channel independently and then stacks
    # the result.
    s1 = _auto_contrast_channel(img, 0, cutoff)
    s2 = _auto_contrast_channel(img, 1, cutoff)
    s3 = _auto_contrast_channel(img, 2, cutoff)
    contrasted_img = np.stack([s1, s2, s3], axis=-1)
    return contrasted_img.astype(img.dtype)


@PIPELINES.register_module()
class AutoContrast(object):
    """Auto adjust image contrast.

    Args:
        prob (float): The probability for performing invert therefore should
             be in range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, prob=0.5):
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.prob = prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        img_contrasted = auto_contrast(img)
        return img_contrasted.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class Identity(object):
    """Identity Mapping (do nothing).

    Args:
        prob (float): The probability for performing identity mapping.
    """

    def __init__(self, prob=0.5):
        self.prob = prob

    def __call__(self, img):
        return img

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class Invert(object):
    """Invert images.

    Args:
        prob (float): The probability for performing invert therefore should
             be in range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, prob=0.5):
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.prob = prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        img_inverted = mmcv.iminvert(img)
        return img_inverted.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class Equalize(object):
    """Equalize the image histogram.

    Args:
        prob (float): The probability for performing invert therefore should
             be in range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, prob=0.5):
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.prob = prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        img_equalized = mmcv.imequalize(img)
        return img_equalized.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class Solarize(object):
    """Solarize images (invert all pixel values above a threshold).

    Args:
        thr (int | float): The threshold above which the pixels value will be
            inverted.
        prob (float): The probability for solarizing therefore should be in
            range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, thr, prob=0.5):
        assert isinstance(thr, (int, float)), 'The thr type must '\
            f'be int or float, but got {type(thr)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.thr = thr
        self.prob = prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        img_solarized = mmcv.solarize(img, thr=self.thr)
        return img_solarized.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(thr={self.thr}, '
        repr_str += f'prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class SolarizeAdd(object):
    """SolarizeAdd images (add a certain value to pixels below a threshold).

    Args:
        magnitude (int | float): The value to be added to pixels below the thr.
        thr (int | float): The threshold below which the pixels value will be
            adjusted.
        prob (float): The probability for solarizing therefore should be in
            range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, magnitude, thr=128, prob=0.5):
        assert isinstance(magnitude, (int, float)), 'The thr magnitude must '\
            f'be int or float, but got {type(magnitude)} instead.'
        assert isinstance(thr, (int, float)), 'The thr type must '\
            f'be int or float, but got {type(thr)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.magnitude = magnitude
        self.thr = thr
        self.prob = prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        img_solarized = np.where(img < self.thr,
                                    np.minimum(img + self.magnitude, 255),
                                    img)
        return img_solarized.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'thr={self.thr}, '
        repr_str += f'prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class Posterize(object):
    """Posterize images (reduce the number of bits for each color channel).

    Args:
        bits (int | float): Number of bits for each pixel in the output img,
            which should be less or equal to 8.
        prob (float): The probability for posterizing therefore should be in
            range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, bits, prob=0.5):
        assert bits <= 8, f'The bits must be less than 8, got {bits} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.bits = int(bits)
        self.prob = prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        img_posterized = mmcv.posterize(img, bits=self.bits)
        return img_posterized.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(bits={self.bits}, '
        repr_str += f'prob={self.prob})'
        return repr_str


@PIPELINES.register_module()
class Contrast(object):
    """Adjust images contrast.

    Args:
        magnitude (int | float): The magnitude used for adjusting contrast. A
            positive magnitude would enhance the contrast and a negative
            magnitude would make the image grayer. A magnitude=0 gives the
            origin img.
        prob (float): The probability for performing contrast adjusting
            therefore should be in range [0, 1]. Defaults to 0.5.
        random_negative_prob (float): The probability that turns the magnitude
            negative, which should be in range [0,1]. Defaults to 0.5.
    """

    def __init__(self, magnitude, prob=0.5, random_negative_prob=0.5):
        assert isinstance(magnitude, (int, float)), 'The magnitude type must '\
            f'be int or float, but got {type(magnitude)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.magnitude = magnitude
        self.prob = prob
        self.random_negative_prob = random_negative_prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        magnitude = random_negative(self.magnitude, self.random_negative_prob)
        img_contrasted = mmcv.adjust_contrast(img, factor=1 + magnitude)
        return img_contrasted.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'random_negative_prob={self.random_negative_prob})'
        return repr_str


@PIPELINES.register_module()
class ColorTransform(object):
    """Adjust images color balance.

    Args:
        magnitude (int | float): The magnitude used for color transform. A
            positive magnitude would enhance the color and a negative magnitude
            would make the image grayer. A magnitude=0 gives the origin img.
        prob (float): The probability for performing ColorTransform therefore
            should be in range [0, 1]. Defaults to 0.5.
        random_negative_prob (float): The probability that turns the magnitude
            negative, which should be in range [0,1]. Defaults to 0.5.
    """

    def __init__(self, magnitude, prob=0.5, random_negative_prob=0.5):
        assert isinstance(magnitude, (int, float)), 'The magnitude type must '\
            f'be int or float, but got {type(magnitude)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.magnitude = magnitude
        self.prob = prob
        self.random_negative_prob = random_negative_prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        magnitude = random_negative(self.magnitude, self.random_negative_prob)
        img_color_adjusted = mmcv.adjust_color(img, alpha=1 + magnitude)
        return img_color_adjusted.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'random_negative_prob={self.random_negative_prob})'
        return repr_str


@PIPELINES.register_module()
class Brightness(object):
    """Adjust images brightness.

    Args:
        magnitude (int | float): The magnitude used for adjusting brightness. A
            positive magnitude would enhance the brightness and a negative
            magnitude would make the image darker. A magnitude=0 gives the
            origin img.
        prob (float): The probability for performing contrast adjusting
            therefore should be in range [0, 1]. Defaults to 0.5.
        random_negative_prob (float): The probability that turns the magnitude
            negative, which should be in range [0,1]. Defaults to 0.5.
    """

    def __init__(self, magnitude, prob=0.5, random_negative_prob=0.5):
        assert isinstance(magnitude, (int, float)), 'The magnitude type must '\
            f'be int or float, but got {type(magnitude)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.magnitude = magnitude
        self.prob = prob
        self.random_negative_prob = random_negative_prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        magnitude = random_negative(self.magnitude, self.random_negative_prob)
        img_brightened = mmcv.adjust_brightness(img, factor=1 + magnitude)
        return img_brightened.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'random_negative_prob={self.random_negative_prob})'
        return repr_str


def adjust_sharpness(img, factor=1., kernel=None):
    """Adjust image sharpness.
    This function controls the sharpness of an image. An
    enhancement factor of 0.0 gives a blurred image. A
    factor of 1.0 gives the original image. And a factor
    of 2.0 gives a sharpened image. It blends the source
    image and the degenerated mean image:
    .. math::
        output = img * factor + degenerated * (1 - factor)
    Args:
        img (ndarray): Image to be sharpened. BGR order.
        factor (float): Same as :func:`mmcv.adjust_brightness`.
        kernel (np.ndarray, optional): Filter kernel to be applied on the img
            to obtain the degenerated img. Defaults to None.
    Note:
        No value sanity check is enforced on the kernel set by users. So with
        an inappropriate kernel, the ``adjust_sharpness`` may fail to perform
        the function its name indicates but end up performing whatever
        transform determined by the kernel.
    Returns:
        ndarray: The sharpened image.
    """

    if kernel is None:
        # adopted from PIL.ImageFilter.SMOOTH
        kernel = np.array([[1., 1., 1.], [1., 5., 1.], [1., 1., 1.]]) / 13
    assert isinstance(kernel, np.ndarray), \
        f'kernel must be of type np.ndarray, but got {type(kernel)} instead.'
    assert kernel.ndim == 2, \
        f'kernel must have a dimension of 2, but got {kernel.ndim} instead.'

    degenerated = cv2.filter2D(img, -1, kernel)
    sharpened_img = cv2.addWeighted(
        img.astype(np.float32), factor, degenerated.astype(np.float32),
        1 - factor, 0)
    sharpened_img = np.clip(sharpened_img, 0, 255)
    return sharpened_img.astype(img.dtype)


@PIPELINES.register_module()
class Sharpness(object):
    """Adjust images sharpness.

    Args:
        magnitude (int | float): The magnitude used for adjusting sharpness. A
            positive magnitude would enhance the sharpness and a negative
            magnitude would make the image bulr. A magnitude=0 gives the
            origin img.
        prob (float): The probability for performing contrast adjusting
            therefore should be in range [0, 1]. Defaults to 0.5.
        random_negative_prob (float): The probability that turns the magnitude
            negative, which should be in range [0,1]. Defaults to 0.5.
    """

    def __init__(self, magnitude, prob=0.5, random_negative_prob=0.5):
        assert isinstance(magnitude, (int, float)), 'The magnitude type must '\
            f'be int or float, but got {type(magnitude)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'
        assert 0 <= random_negative_prob <= 1.0, 'The random_negative_prob ' \
            f'should be in range [0,1], got {random_negative_prob} instead.'

        self.magnitude = magnitude
        self.prob = prob
        self.random_negative_prob = random_negative_prob

    def __call__(self, img):
        if np.random.rand() > self.prob:
            return img
        magnitude = random_negative(self.magnitude, self.random_negative_prob)
        img_sharpened = adjust_sharpness(img, factor=1 + magnitude)
        return img_sharpened.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(magnitude={self.magnitude}, '
        repr_str += f'prob={self.prob}, '
        repr_str += f'random_negative_prob={self.random_negative_prob})'
        return repr_str


def cutout(img, shape, pad_val=0):
    """Randomly cut out a rectangle from the original img.
    Args:
        img (ndarray): Image to be cutout.
        shape (int | tuple[int]): Expected cutout shape (h, w). If given as a
            int, the value will be used for both h and w.
        pad_val (int | float | tuple[int | float]): Values to be filled in the
            cut area. Defaults to 0.
    Returns:
        ndarray: The cutout image.
    """

    channels = 1 if img.ndim == 2 else img.shape[2]
    if isinstance(shape, int):
        cut_h, cut_w = shape, shape
    else:
        assert isinstance(shape, tuple) and len(shape) == 2, \
            f'shape must be a int or a tuple with length 2, but got type ' \
            f'{type(shape)} instead.'
        cut_h, cut_w = shape
    if isinstance(pad_val, (int, float)):
        pad_val = tuple([pad_val] * channels)
    elif isinstance(pad_val, tuple):
        assert len(pad_val) == channels, \
            'Expected the num of elements in tuple equals the channels' \
            'of input image. Found {} vs {}'.format(
                len(pad_val), channels)
    else:
        raise TypeError(f'Invalid type {type(pad_val)} for `pad_val`')

    img_h, img_w = img.shape[:2]
    y0 = np.random.uniform(img_h)
    x0 = np.random.uniform(img_w)

    y1 = int(max(0, y0 - cut_h / 2.))
    x1 = int(max(0, x0 - cut_w / 2.))
    y2 = min(img_h, y1 + cut_h)
    x2 = min(img_w, x1 + cut_w)

    if img.ndim == 2:
        patch_shape = (y2 - y1, x2 - x1)
    else:
        patch_shape = (y2 - y1, x2 - x1, channels)

    img_cutout = img.copy()
    patch = np.array(
        pad_val, dtype=img.dtype) * np.ones(
            patch_shape, dtype=img.dtype)
    img_cutout[y1:y2, x1:x2, ...] = patch

    return img_cutout


@PIPELINES.register_module()
class Cutout(object):
    """Cutout images.

    Args:
        shape (int | float | tuple(int | float)): Expected cutout shape (h, w).
            If given as a single value, the value will be used for
            both h and w.
        pad_val (int, Sequence[int]): Pixel pad_val value for constant fill.
            If it is a sequence, it must have the same length with the image
            channels. Defaults to 128.
        prob (float): The probability for performing cutout therefore should
            be in range [0, 1]. Defaults to 0.5.
    """

    def __init__(self, shape, pad_val=128, prob=0.5):
        if isinstance(shape, float):
            shape = int(shape)
        elif isinstance(shape, tuple):
            shape = tuple(int(i) for i in shape)
        elif not isinstance(shape, int):
            raise TypeError(
                'shape must be of '
                f'type int, float or tuple, got {type(shape)} instead')
        if isinstance(pad_val, int):
            pad_val = tuple([pad_val] * 3)
        elif isinstance(pad_val, Sequence):
            assert len(pad_val) == 3, 'pad_val as a tuple must have 3 ' \
                f'elements, got {len(pad_val)} instead.'
        assert 0 <= prob <= 1.0, 'The prob should be in range [0,1], ' \
            f'got {prob} instead.'

        self.shape = shape
        self.pad_val = tuple(pad_val)
        self.prob = prob

    def __call__(self, img):
        """ assume the default img is numpy.array """
        if np.random.rand() > self.prob:
            return img
        if isinstance(img, Image.Image):
            img = np.array(img)
            img = cutout(img, self.shape, pad_val=self.pad_val)
            return Image.fromarray(img.astype(np.uint8))
        else:
            img_cutout = cutout(img, self.shape, pad_val=self.pad_val)
            return img_cutout.astype(img.dtype)

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += f'(shape={self.shape}, '
        repr_str += f'pad_val={self.pad_val}, '
        repr_str += f'prob={self.prob})'
        return repr_str


# yapf: disable
AUTOAUG_POLICIES = {
    # Policy for ImageNet, refers to
    # https://github.com/DeepVoltaire/AutoAugment/blame/master/autoaugment.py
    'imagenet': [
        [dict(type='Posterize', bits=4, prob=0.4),             dict(type='Rotate', angle=30., prob=0.6)],
        [dict(type='Solarize', thr=256 / 9 * 4, prob=0.6),     dict(type='AutoContrast', prob=0.6)],
        [dict(type='Equalize', prob=0.8),                      dict(type='Equalize', prob=0.6)],
        [dict(type='Posterize', bits=5, prob=0.6),             dict(type='Posterize', bits=5, prob=0.6)],
        [dict(type='Equalize', prob=0.4),                      dict(type='Solarize', thr=256 / 9 * 5, prob=0.2)],
        [dict(type='Equalize', prob=0.4),                      dict(type='Rotate', angle=30 / 9 * 8, prob=0.8)],
        [dict(type='Solarize', thr=256 / 9 * 6, prob=0.6),     dict(type='Equalize', prob=0.6)],
        [dict(type='Posterize', bits=6, prob=0.8),             dict(type='Equalize', prob=1.)],
        [dict(type='Rotate', angle=10., prob=0.2),             dict(type='Solarize', thr=256 / 9, prob=0.6)],
        [dict(type='Equalize', prob=0.6),                      dict(type='Posterize', bits=5, prob=0.4)],
        [dict(type='Rotate', angle=30 / 9 * 8, prob=0.8),      dict(type='ColorTransform', magnitude=0., prob=0.4)],
        [dict(type='Rotate', angle=30., prob=0.4),             dict(type='Equalize', prob=0.6)],
        [dict(type='Equalize', prob=0.0),                      dict(type='Equalize', prob=0.8)],
        [dict(type='Invert', prob=0.6),                        dict(type='Equalize', prob=1.)],
        [dict(type='ColorTransform', magnitude=0.4, prob=0.6), dict(type='Contrast', magnitude=0.8, prob=1.)],
        [dict(type='Rotate', angle=30 / 9 * 8, prob=0.8),      dict(type='ColorTransform', magnitude=0.2, prob=1.)],
        [dict(type='ColorTransform', magnitude=0.8, prob=0.8), dict(type='Solarize', thr=256 / 9 * 2, prob=0.8)],
        [dict(type='Sharpness', magnitude=0.7, prob=0.4),      dict(type='Invert', prob=0.6)],
        [dict(type='Shear', magnitude=0.3 / 9 * 5, prob=0.6, direction='horizontal'), dict(type='Equalize', prob=1.)],
        [dict(type='ColorTransform', magnitude=0., prob=0.4),  dict(type='Equalize', prob=0.6)],
        [dict(type='Equalize', prob=0.4),                      dict(type='Solarize', thr=256 / 9 * 5, prob=0.2)],
        [dict(type='Solarize', thr=256 / 9 * 4, prob=0.6),     dict(type='AutoContrast', prob=0.6)],
        [dict(type='Invert', prob=0.6),                        dict(type='Equalize', prob=1.)],
        [dict(type='ColorTransform', magnitude=0.4, prob=0.6), dict(type='Contrast', magnitude=0.8, prob=1.)],
        [dict(type='Equalize', prob=0.8),                      dict(type='Equalize', prob=0.6)],
    ],
}


RANDAUG_POLICIES = {
    # Refers to `_RAND_INCREASING_TRANSFORMS` in pytorch-image-models
    'timm_increasing': [
        dict(type='AutoContrast'),
        dict(type='Equalize'),
        dict(type='Invert'),
        dict(type='Rotate', magnitude_range=(0, 30)),
        dict(type='Posterize', magnitude_range=(4, 0)),
        dict(type='Solarize', magnitude_range=(256, 0)),
        dict(type='SolarizeAdd', magnitude_range=(0, 110)),
        dict(type='ColorTransform', magnitude_range=(0, 0.9)),
        dict(type='Contrast', magnitude_range=(0, 0.9)),
        dict(type='Brightness', magnitude_range=(0, 0.9)),
        dict(type='Sharpness', magnitude_range=(0, 0.9)),
        dict(type='Shear', magnitude_range=(0, 0.3), direction='horizontal'),
        dict(type='Shear', magnitude_range=(0, 0.3), direction='vertical'),
        dict(type='Translate', magnitude_range=(0, 0.45), direction='horizontal'),
        dict(type='Translate', magnitude_range=(0, 0.45), direction='vertical'),
    ],
}
