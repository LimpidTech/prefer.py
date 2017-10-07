import mock

from prefer import events


def test_event_emitter_emits_event():
    mock_args = ['update', 1]
    mock_kwargs = {'mock': 'kwargs'}

    handler = mock.MagicMock()

    emitter = events.Emitter()
    emitter.bind('update', handler)

    emitter.emit(*mock_args, **mock_kwargs)

    handler.assert_called_once_with(*mock_args, **mock_kwargs)
