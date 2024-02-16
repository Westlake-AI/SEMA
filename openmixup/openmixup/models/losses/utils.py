import functools

import torch
import torch.nn.functional as F


def weight_reduce_loss(loss, weight=None, reduction='mean', avg_factor=None):
    """Apply element-wise weight and reduce loss.

    Args:
        loss (Tensor): Element-wise loss tensor.
        weight (Tensor): Element-wise weights.
        reduction (str): Same as built-in losses of PyTorch. Options are "none",
            "mean" and "sum".
        avg_factor (float): Avarage factor when computing the mean of losses.

    Returns:
        Tensor: Processed loss values.
    """
    # if weight is specified, apply element-wise weight
    if weight is not None:
        loss = loss * weight

    reduction_enum = F._Reduction.get_enum(reduction)
    # if avg_factor is not specified, just reduce the loss
    if avg_factor is None:
        # none: 0, elementwise_mean:1, sum: 2
        if reduction_enum == 1:
            loss = loss.mean()
        elif reduction_enum == 2:
            loss = loss.sum()
    else:
        # if reduction is 'mean', then average the loss by avg_factor
        if reduction_enum == 1:
            loss = loss.sum() / avg_factor
        # if reduction is 'none', then do nothing; otherwise raise an error
        elif reduction != 0:
            raise ValueError('avg_factor can not be used with reduction="sum"')
    return loss


def weighted_loss(loss_func):
    """Create a weighted version of a given loss function.

    To use this decorator, the loss function must have the signature like
    ``loss_func(pred, target, **kwargs)``. The function only needs to compute
    element-wise loss without any reduction. This decorator will add weight
    and reduction arguments to the function. The decorated function will have
    the signature like ``loss_func(pred, target, weight=None, reduction='mean',
    avg_factor=None, **kwargs)``.

    :Example:

    >>> import torch
    >>> @weighted_loss
    >>> def l1_loss(pred, target):
    >>>     return (pred - target).abs()

    >>> pred = torch.Tensor([0, 2, 3])
    >>> target = torch.Tensor([1, 1, 1])
    >>> weight = torch.Tensor([1, 0, 1])

    >>> l1_loss(pred, target)
    tensor(1.3333)
    >>> l1_loss(pred, target, weight)
    tensor(1.)
    >>> l1_loss(pred, target, reduction='none')
    tensor([1., 1., 2.])
    >>> l1_loss(pred, target, weight, avg_factor=2)
    tensor(1.5000)
    """

    @functools.wraps(loss_func)
    def wrapper(pred,
                target,
                weight=None,
                reduction='mean',
                avg_factor=None,
                **kwargs):
        # get element-wise loss
        loss = loss_func(pred, target, **kwargs)
        loss = weight_reduce_loss(loss, weight, reduction, avg_factor)
        return loss

    return wrapper


def convert_to_one_hot(targets, num_classes=None):
    """This function converts target class indices to one-hot vectors, given
    the number of classes.

    Args:
        targets (Tensor): The ground truth label of the prediction
                with shape (N, 1)
        num_classes (int): the number of classes.

    Returns:
        Tensor: Processed loss values.
    """
    # already as onehot [N, C]
    if targets.dim() != 1 and not (targets.dim() == 2 and targets.shape[1] == 1):
        return targets
    # targets are inputted as class integers: convert to onehot
    assert num_classes is not None
    assert (torch.max(targets).item() <
            num_classes), 'Class Index must be less than number of classes'
    
    one_hot_targets = F.one_hot(targets, num_classes=num_classes)
    # one_hot_targets = torch.zeros((targets.reshape(-1, 1).shape[0], num_classes),
    #                               dtype=torch.long, device=targets.device)
    # one_hot_targets.scatter_(1, targets.long(), 1)
    return one_hot_targets
