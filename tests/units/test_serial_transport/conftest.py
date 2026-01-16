import pytest


@pytest.fixture
def serial_mock(mocker):
    return mocker.patch("transport.serial_port.serial.Serial")


@pytest.fixture
def serial_transport(serial_mock):
    from transport.serial import SerialTransport

    return SerialTransport(
        port="COM14",
        baudrate=1_000_000,
    )
