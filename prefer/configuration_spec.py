import mock
import unittest

from prefer import configuration


def test_configuration_object_raises_error_on_save_until_implemented():
    has_seen_expected_error = False

    try:
        configuration.Configuration().save()
    except Exception as e:
        has_seen_expected_error = isinstance(e, NotImplementedError)

    assert has_seen_expected_error is True


def test_configuration_object_supports_context_assignment_via_setitem():
    conf = configuration.Configuration(context=mock.MagicMock())
    conf['test'] = 'wat'
    conf.context.__setitem__.assert_called_once_with('test', 'wat')


def test_configuration_object_gets_items_from_context():
    conf = configuration.Configuration(
        loader=None,
        formatter=None,
        context={'test': 'wat'},
    )

    assert conf['test'] == 'wat'


def test_configuration_object_is_empty_if_using_None():
    instance = configuration.Configuration.using(None)

    assert instance == {}
    assert isinstance(instance, configuration.Configuration)


def test_configuration_object_can_be_created_via_using():
    mock_data = {'mock': 'data'}
    instance = configuration.Configuration.using(mock_data)

    assert instance == mock_data
    assert isinstance(instance, configuration.Configuration)


def test_configuration_using_acts_as_identity_function_when_given_same_type():
    instance = configuration.Configuration()
    assert configuration.Configuration.using(instance) is instance


def test_configuration_object_supports_equality_testing():
    conf = configuration.Configuration(formatter=None, loader=None)
    match_dict = {'test': 'wat'}
    conf['test'] = 'wat'

    assert conf == conf
    assert conf == match_dict
    assert configuration.Configuration() != match_dict


def test_configuration_object_deletes_items_from_context():
    context = {'test': 'wat'}
    conf = configuration.Configuration(context=context)
    del conf['test']
    assert 'test' not in context


def test_configuration_object_checks_context_for_containment():
    context = {'test': 'wat'}
    assert 'test' in configuration.Configuration(context=context)


def test_get_returns_item_from_context():
    context = {'test': 'wat'}
    assert 'wat' == configuration.Configuration(context=context).get('test')


def test_get_returns_nested_item_from_context():
    context = {'test': {'nested': {'example': 'wat'}}}
    subject = configuration.Configuration(context=context)

    assert 'wat' == subject.get('test.nested.example')


def test_set_updates_a_nested_value_in_the_context():
    mock_value = {}

    subject = configuration.Configuration()
    subject.set('test.example', mock_value)
    print(subject.context)
    assert mock_value is subject.get('test.example')
