from __future__ import absolute_import

import numpy as np
import tensorflow as tf
import tensornets as nets
import os
import pytest
import random

from tensornets.middles import direct

from distutils.version import LooseVersion


pytestmark = pytest.mark.skipif(
    os.environ.get('CORE_CHANGED', 'True') == 'False',
    reason='Runs only when the relevant files have been modified.')


@pytest.mark.parametrize('net,shape', [
    random.choice([
        (nets.ResNet50, (224, 224, 3)),
        (nets.ResNet101, (224, 224, 3)),
        (nets.ResNet152, (224, 224, 3)),
    ]),
    random.choice([
        (nets.ResNet50v2, (299, 299, 3)),
        (nets.ResNet101v2, (299, 299, 3)),
        (nets.ResNet152v2, (299, 299, 3)),
    ]),
    (nets.ResNet200v2, (224, 224, 3)),
    random.choice([
        (nets.ResNeXt50, (224, 224, 3)),
        (nets.ResNeXt101, (224, 224, 3)),
        (nets.ResNeXt101c64, (224, 224, 3)),
    ]),
    (nets.WideResNet50, (224, 224, 3)),
    (nets.Inception1, (224, 224, 3)),
    (nets.Inception2, (224, 224, 3)),
    (nets.Inception3, (299, 299, 3)),
    (nets.Inception4, (299, 299, 3)),
    (nets.InceptionResNet2, (299, 299, 3)),
    pytest.param(
        nets.NASNetAlarge, (331, 331, 3),
        marks=pytest.mark.xfail(
            LooseVersion(tf.__version__) < LooseVersion('1.3.0'),
            reason='NASNetAlarge requires TensorFlow >= 1.3.0')),
    pytest.param(
        nets.NASNetAmobile, (224, 224, 3),
        marks=pytest.mark.xfail(
            LooseVersion(tf.__version__) < LooseVersion('1.3.0'),
            reason='NASNetAmobile requires TensorFlow >= 1.3.0')),
    random.choice([
        (nets.VGG16, (224, 224, 3)),
        (nets.VGG19, (224, 224, 3)),
    ]),
    random.choice([
        (nets.DenseNet121, (224, 224, 3)),
        (nets.DenseNet169, (224, 224, 3)),
        (nets.DenseNet201, (224, 224, 3)),
    ]),
    random.choice([
        (nets.MobileNet25, (224, 224, 3)),
        (nets.MobileNet50, (224, 224, 3)),
        (nets.MobileNet75, (224, 224, 3)),
        (nets.MobileNet100, (224, 224, 3)),
    ]),
    (nets.SqueezeNet, (224, 224, 3)),
], ids=[
    'ResNet',
    'ResNetv2',
    'ResNet200v2',
    'ResNeXt',
    'WideResNet50',
    'Inception1',
    'Inception2',
    'Inception3',
    'Inception4',
    'InceptionResNet2',
    'NASNetAlarge',
    'NASNetAmobile',
    'VGG',
    'DenseNet',
    'MobileNet',
    'SqueezeNet',
])
def test_classification_basics(net, shape):
    inputs = tf.placeholder(tf.float32, [None] + list(shape))
    model = net(inputs, is_training=False)
    assert isinstance(model, tf.Tensor)

    x = np.random.random((1,) + shape).astype(np.float32)

    with tf.Session() as sess:
        nets.init(model)
        y = model.eval({inputs: x})

    for (a, b) in zip(model.get_middles(), direct(model.aliases[0])[1]):
        assert a.name.endswith(b)

    assert y.shape == (1, 1000)


def test_detection_basics():
    # TODO: Once the roi-pooling dependency is removed,
    # FasterRCNN-related tests should be added.
    inputs = tf.placeholder(tf.float32, [None, 416, 416, 3])
    model1 = nets.YOLOv2(inputs, nets.Darknet19, is_training=False)
    assert isinstance(model1, tf.Tensor)

    model2 = nets.TinyYOLOv2(inputs, nets.TinyDarknet19, is_training=False)
    assert isinstance(model2, tf.Tensor)

    x = np.random.random((1, 733, 490, 3)).astype(np.float32) * 255

    with tf.Session() as sess:
        nets.init([model1, model2])
        y1 = model1.eval({inputs: model1.preprocess(x)})
        y2 = model2.eval({inputs: model2.preprocess(x)})

    boxes1 = model1.get_boxes(y1, x.shape[1:3])
    boxes2 = model2.get_boxes(y2, x.shape[1:3])

    assert len(boxes1) == 20
    assert len(boxes2) == 20
