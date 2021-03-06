from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from caffe2.python import core, workspace
from hypothesis import given

import caffe2.python.hypothesis_test_util as hu
import caffe2.python.serialized_test.serialized_test_util as serial
import hypothesis.strategies as st

import numpy as np
import unittest


class TestTransposeOp(serial.SerializedTestCase):
    @serial.given(
        X=hu.tensor(dtype=np.float32), use_axes=st.booleans(), **hu.gcs)
    def test_transpose(self, X, use_axes, gc, dc):
        ndim = len(X.shape)
        axes = np.arange(ndim)
        np.random.shuffle(axes)

        if (use_axes):
            op = core.CreateOperator(
                "Transpose", ["X"], ["Y"], axes=axes, device_option=gc)
        else:
            op = core.CreateOperator(
                "Transpose", ["X"], ["Y"], device_option=gc)

        def transpose_ref(X):
            if use_axes:
                return [np.transpose(X, axes=axes)]
            else:
                return [np.transpose(X)]

        self.assertReferenceChecks(gc, op, [X], transpose_ref)
        self.assertDeviceChecks(dc, op, [X], [0])
        self.assertGradientChecks(gc, op, [X], 0, [0])

    @unittest.skipIf(not workspace.has_gpu_support, "no gpu support")
    @given(X=hu.tensor(dtype=np.float32), use_axes=st.booleans(),
           **hu.gcs_gpu_only)
    def test_transpose_cudnn(self, X, use_axes, gc, dc):
        ndim = len(X.shape)
        axes = np.arange(ndim)
        np.random.shuffle(axes)

        if (use_axes):
            op = core.CreateOperator(
                "Transpose", ["X"], ["Y"], axes=axes, engine="CUDNN",
                device_option=hu.gpu_do)
        else:
            op = core.CreateOperator(
                "Transpose", ["X"], ["Y"], engine="CUDNN",
                device_option=hu.gpu_do)

        def transpose_ref(X):
            if use_axes:
                return [np.transpose(X, axes=axes)]
            else:
                return [np.transpose(X)]

        self.assertReferenceChecks(hu.gpu_do, op, [X], transpose_ref)
        self.assertGradientChecks(hu.gpu_do, op, [X], 0, [0])


if __name__ == "__main__":
    unittest.main()
