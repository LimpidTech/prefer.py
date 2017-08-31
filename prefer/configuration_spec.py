import unittest

from prefer import configuration


def test_configuration_object_can_be_compared_to_dictionary():
    assert configuration.Configuration() == {}


def test_configuration_object_raises_error_on_save_until_implemented():
    has_seen_expected_error = False

    try:
        configuration.Configuration().save()
    except Exception as e:
        has_seen_expected_error = isinstance(e, NotImplementedError)

    assert has_seen_expected_error is True
