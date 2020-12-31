# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Converters for ONNX operators.
"""

import numpy as np
from onnxconverter_common.registration import register_converter
import torch

from .. import constants
from .._base_operator import BaseOperator
from .._pipeline_implementations import Concat


class Cast(BaseOperator, torch.nn.Module):
    def __init__(self, to_type):
        super(Cast, self).__init__()

        assert to_type is not None

        self._to_type = to_type

    def forward(self, x):
        if self._to_type == 1:  # Cast to float
            return x.float()
        elif self._to_type == 7:  # Cast to long
            return x.long()
        elif self._to_type == 11:  # Cast to double
            return x.double()
        else:
            raise RuntimeError(
                "Cast to ONNX type {} not supported yet. Please fill an issue at https://github.com/microsoft/hummingbird".format(
                    self._to_type
                )
            )


class Reshape(BaseOperator, torch.nn.Module):
    def __init__(self, shape):
        super(Reshape, self).__init__()

        self.shape = shape

    def forward(self, x):
        return torch.reshape(x, self.shape)


class Sum(BaseOperator, torch.nn.Module):
    def __init__(self):
        super(Sum, self).__init__()

    def forward(self, x):
        return torch.sum(x).view(1)


class Add(BaseOperator, torch.nn.Module):
    def __init__(self, val):
        super(Add, self).__init__()

        self.val = torch.nn.Parameter(torch.FloatTensor(val), requires_grad=False)

    def forward(self, *x):
        if len(x) == 1:
            return torch.add(*x, self.val)
        return torch.add(*x)


class Less(BaseOperator, torch.nn.Module):
    def __init__(self, val):
        super(Less, self).__init__()

        self.val = val

    def forward(self, x):
        return torch.lt(x, self.val)


class Neg(BaseOperator, torch.nn.Module):
    def __init__(self):
        super(Neg, self).__init__()

    def forward(self, x):
        return torch.neg(x).view(-1)


class Abs(BaseOperator, torch.nn.Module):
    def __init__(self):
        super(Abs, self).__init__()

    def forward(self, x):
        return torch.abs(x)


class Mul(BaseOperator, torch.nn.Module):
    def __init__(self, val):
        super(Mul, self).__init__()

        self.val = val

    def forward(self, x):
        return torch.mul(x, self.val)


class Div(BaseOperator, torch.nn.Module):
    def __init__(self):
        super(Div, self).__init__()

    def forward(self, *x):
        return torch.divide(*x)


def convert_onnx_cast(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Cast`.

    Args:
        operator: An operator wrapping a `ai.onnx.Cast` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    to_type = None

    for attr in operator.raw_operator.origin.attribute:
        if attr.name == "to":
            to_type = attr.i

    # Generate the model.
    return Cast(to_type)


def convert_onnx_concat(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Concat`.

    Args:
        operator: An operator wrapping a `ai.onnx.Concat` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    # Generate the model.
    return Concat()


def convert_onnx_reshape(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Reshape`.

    Args:
        operator: An operator wrapping a `ai.onnx.Reshape` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    shape = []
    initializers = extra_config[constants.ONNX_INITIALIZERS]
    shape = list(initializers[operator.raw_operator.origin.input[1]].int64_data)

    # Generate the model.
    return Reshape(shape)


def convert_onnx_sum(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Sum`.

    Args:
        operator: An operator wrapping a `ai.onnx.Sum` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    # Generate the model.
    return Sum()


def convert_onnx_add(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Add`.

    Args:
        operator: An operator wrapping a `ai.onnx.Add` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    val = extra_config[constants.ONNX_INITIALIZERS]["cst1"]

    # Generate the model.
    return Add(val.float_data)


def convert_onnx_neg(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Neg`.

    Args:
        operator: An operator wrapping a `ai.onnx.Neg` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    # Generate the model.
    return Neg()


def convert_onnx_abs(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Abs`.

    Args:
        operator: An operator wrapping a `ai.onnx.Abs` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    # Generate the model.
    return Abs()


def convert_onnx_mul(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Mul`.

    Args:
        operator: An operator wrapping a `ai.onnx.Mul` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    val = extra_config[constants.ONNX_INITIALIZERS]["cst3"]

    # Generate the model.
    return Mul(val.float_data[0])


def convert_onnx_div(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Div`.

    Args:
        operator: An operator wrapping a `ai.onnx.Div` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    # Generate the model.
    return Div()


def convert_onnx_less(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Less`.

    Args:
        operator: An operator wrapping a `ai.onnx.Less` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    val = extra_config[constants.ONNX_INITIALIZERS]["cst0"]

    # Generate the model.
    return Less(val.float_data[0])


register_converter("ONNXMLAbs", convert_onnx_abs)
register_converter("ONNXMLAdd", convert_onnx_add)
register_converter("ONNXMLCast", convert_onnx_cast)
register_converter("ONNXMLConcat", convert_onnx_concat)
register_converter("ONNXMLDiv", convert_onnx_div)
register_converter("ONNXMLLess", convert_onnx_less)
register_converter("ONNXMLMul", convert_onnx_mul)
register_converter("ONNXMLNeg", convert_onnx_neg)
register_converter("ONNXMLReshape", convert_onnx_reshape)
register_converter("ONNXMLSum", convert_onnx_sum)
