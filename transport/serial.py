import serial
import enum


class SerialConfigurationError(Exception):
    pass


class SerialConfiguration(enum.IntEnum):
    BAUD_9600 = 9600
    BAUD_115200 = 115200
    BAUD_57600 = 57600
    BAUD_250_000 = 250000
    BAUD_500_000 = 500000
    BAUD_1_000_000 = 1000000
    BAUD_2_000_000 = 2000000


class SerialTransport:
    def __init__(
        self,
        port: str,
        baudrate: int = SerialConfiguration.BAUD_1_000_000,
        *,
        timeout: float = 0.01,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    ):
        self._validate_config(port, baudrate, timeout)

        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
            )
        except serial.SerialException as e:
            raise SerialConfigurationError(
                f"Failed to initialize serial port {port}"
            ) from e

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def open(self):
        if not self._serial.is_open:
            self._serial.open()

    def close(self):
        if self._serial.is_open:
            self._serial.close()

    def send(self, data: bytes):
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes")

        self._serial.write(data)

    def receive(self, max_bytes: int = 64) -> bytes:
        waiting = self._serial.in_waiting
        size = min(waiting, max_bytes) if waiting else 1
        return self._serial.read(size)

    @staticmethod
    def _validate_config(port, baudrate, timeout):
        if not isinstance(port, str):
            raise SerialConfigurationError("port must be a string")

        try:
            SerialConfiguration(baudrate)
        except Exception as exc:
            raise SerialConfigurationError(f"Unsupported baudrate: {baudrate}") from exc

        if timeout is None or timeout < 0:
            raise SerialConfigurationError("timeout must be >= 0")
