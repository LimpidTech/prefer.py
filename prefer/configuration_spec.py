import unittest

from prefer import configuration


def test_configuration_object_can_be_compared_to_dictionary():
    assert configuration.Configuration() == {}
