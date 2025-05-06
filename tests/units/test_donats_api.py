import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from gunlinuxbot.donats.donats import DonatApi
from gunlinuxbot.models.donats import AlertEvent, DonationTypes, BillingSystem


@pytest.fixture
def mock_sio():
    mock = AsyncMock()
    # Store event handlers
    mock._event_handlers = {}  # noqa: SLF001

    def mock_on(event_name):
        def wrapper(func):
            mock._event_handlers[event_name] = func  # noqa: SLF001
            return func

        return wrapper

    def mock_event(func):
        mock._event_handlers['message'] = func  # noqa: SLF001
        return func

    mock.on = Mock(side_effect=mock_on)
    mock.event = Mock(side_effect=mock_event)
    return mock


@pytest.fixture
def mock_handler():
    return AsyncMock()


@pytest.fixture
def donat_api(mock_handler, mock_sio):
    with patch('socketio.AsyncClient', return_value=mock_sio):
        return DonatApi(token='test_token', handler=mock_handler)  # noqa: S106


@pytest.fixture
def donat_api_no_handler(mock_sio):
    with patch('socketio.AsyncClient', return_value=mock_sio):
        return DonatApi(token='test_token', handler=None)  # noqa: S106


async def test_donat_api_init(donat_api, mock_sio, mock_handler):
    # Test initialization
    assert donat_api.token == 'test_token'  # noqa: S105
    assert donat_api.handler == mock_handler
    assert donat_api.sio == mock_sio

    # Verify event handlers were registered
    assert 'connect' in mock_sio._event_handlers  # noqa: SLF001
    assert '*' in mock_sio._event_handlers  # noqa: SLF001
    assert 'donation' in mock_sio._event_handlers  # noqa: SLF001
    assert 'message' in mock_sio._event_handlers  # noqa: SLF001


async def test_donat_api_run(donat_api, mock_sio):
    await donat_api.run()
    mock_sio.connect.assert_called_once_with(
        'wss://socket.donationalerts.ru:443',
        transports='websocket',
    )
    mock_sio.wait.assert_called_once()


async def test_donat_api_on_connect(donat_api, mock_sio):  # noqa: ARG001
    on_connect = mock_sio._event_handlers['connect']  # noqa: SLF001
    await on_connect()
    mock_sio.emit.assert_called_once_with(
        'add-user',
        {'token': 'test_token', 'type': 'alert_widget'},
    )


async def test_donat_api_on_message(donat_api, mock_sio, mock_handler):  # noqa: ARG001
    on_message = mock_sio._event_handlers['donation']  # noqa: SLF001
    # Test valid donation message
    valid_data = {
        'id': 123,
        'alert_type': '1',  # DonationTypes.DONATION
        'billing_system': 'TWITCH',
        'username': 'test_user',
        'amount': 100.0,
        'amount_formatted': '100.00',
        'currency': 'USD',
        'message': 'Test donation',
        'date_created': '2024-01-01',
        '_is_test_alert': False,
    }
    await on_message(json.dumps(valid_data))
    mock_handler.assert_called_once()
    call_args = mock_handler.call_args[0][0]
    assert isinstance(call_args, AlertEvent)
    assert call_args.id == valid_data['id']
    assert call_args.username == valid_data['username']

    # Test invalid message
    mock_handler.reset_mock()
    await on_message(json.dumps({'invalid': 'data'}))
    mock_handler.assert_not_called()


async def test_donat_api_on_message_no_handler(donat_api_no_handler, mock_sio):  # noqa: ARG001
    on_message = mock_sio._event_handlers['donation']  # noqa: SLF001
    # Test valid donation message with no handler
    valid_data = {
        'id': 123,
        'alert_type': '1',
        'billing_system': 'TWITCH',
        'username': 'test_user',
        'amount': 100.0,
        'amount_formatted': '100.00',
        'currency': 'USD',
        'message': 'Test donation',
        'date_created': '2024-01-01',
        '_is_test_alert': False,
    }
    # Should log critical message but not raise error
    await on_message(json.dumps(valid_data))


async def test_donat_api_catch_all(donat_api, mock_sio):  # noqa: ARG001
    catch_all = mock_sio._event_handlers['*']  # noqa: SLF001
    # Test catch_all with some event
    mock_event = AlertEvent(
        id=123,
        alert_type=DonationTypes.DONATION,
        billing_system=BillingSystem.TWITCH,
        username='test_user',
        amount=100.0,
        amount_formatted='100.00',
        currency='USD',
        message='Test donation',
        date_created='2024-01-01',
        _is_test_alert=False,
    )
    await catch_all(mock_event, 'test_data')  # Should just log without error


async def test_donat_api_message_event(donat_api, mock_sio):  # noqa: ARG001
    message_handler = mock_sio._event_handlers['message']  # noqa: SLF001
    await message_handler('test message')  # Should just log without error
