import pytest


def test_port_value_is_none():
    from transport.serial import SerialTransport

    with pytest.raises(ValueError):
        SerialTransport(port=None, baudrate=1_000_000)


def test_port_is_not_str():
    from transport.serial import SerialTransport

    with pytest.raises(TypeError):
        SerialTransport(port=14, baudrate=1_000_000)


def test_baudrate_is_not_int():
    from transport.serial import SerialTransport

    with pytest.raises(ValueError):
        SerialTransport(port="COM14", baudrate="12345")


def test_baudrate_not_in_scope():
    from transport.serial import SerialTransport

    with pytest.raises(ValueError):
        SerialTransport(port="12", baudrate=123456)


def test_timeout_is_none():
    from transport.serial import SerialTransport

    with pytest.raises(ValueError):
        SerialTransport(port="COM14", baudrate=1_000_000, timeout=None)


def test_timeout_is_not_number():
    from transport.serial import SerialTransport

    with pytest.raises(TypeError):
        SerialTransport(port="COM14", baudrate=1_000_000, timeout="12")


def test_timeout_is_not_positive():
    from transport.serial import SerialTransport

    with pytest.raises(ValueError):
        SerialTransport(port="COM14", baudrate=1_000_000, timeout=-1)


def test_serial_port_is_configure_uncorrectly(serial_mock, serial_transport):
    from serial import SerialException

    serial_mock.side_effect = SerialException("Mocked configuration error")
    with pytest.raises(SerialException):
        serial_mock.assert_called_once_with(
            port=14,
            baudrate=1_000_000,
            timeout=0.1,
            bytesize=serial_mock.ANY,
            parity=serial_mock.ANY,
            stopbits=serial_mock.ANY,
        )


def test_serial_port_is_configure_correctly(serial_mock, serial_transport):
    serial_mock.assert_called_once_with(
        port="COM14",
        baudrate=1_000_000,
        timeout=0.1,
        bytesize=serial_mock.ANY,
        parity=serial_mock.ANY,
        stopbits=serial_mock.ANY,
    )


def test_serial_port_open(serial_mock, serial_transport):
    fake_serial = serial_mock.return_value

    serial_transport.open()

    fake_serial.open.assert_called_once()
