import logging
import enum
from typing import List, Optional

from .protocol import ServoPacket


_LOGGER = logging.getLogger(__name__)


class ServoParsingError(Exception):
    """Custom exception for handling parsing errors in servo frames."""

    pass


class FrameIndex(enum.IntEnum):
    HEADER_START = 0
    HEADER_END = 2
    SERVO_ID = HEADER_END
    LENGTH = SERVO_ID + 1
    INSTRUCTION = LENGTH + 1
    PARAMS_START = INSTRUCTION + 1


class DeserializerState(enum.Enum):
    WAIT_HEADER_1 = enum.auto()
    WAIT_HEADER_2 = enum.auto()
    WAIT_ID = enum.auto()
    WAIT_LENGTH = enum.auto()
    WAIT_PAYLOAD = enum.auto()
    WAIT_CHECKSUM = enum.auto()


class PacketDeserializer:

    HEADER_BYTE = 0xFF

    MAX_FRAME_LENGTH = 64
    MAX_PARAMS_LENGTH = 60

    def __init__(self):
        self._state = DeserializerState.WAIT_HEADER_1
        self._buffer = bytearray()
        self._remaining_payload = 0

    def feed(self, data: bytes) -> List["ServoPacket"]:
        packets: List["ServoPacket"] = []

        for byte in data:
            packet = self._process_byte(byte)
            if packet is not None:
                packets.append(packet)

        return packets

    def _process_byte(self, byte: int) -> Optional["ServoPacket"]:
        match self._state:
            case DeserializerState.WAIT_HEADER_1:
                return self._handle_wait_header_1(byte)
            case DeserializerState.WAIT_HEADER_2:
                return self._handle_wait_header_2(byte)
            case DeserializerState.WAIT_ID:
                return self._handle_wait_id(byte)
            case DeserializerState.WAIT_LENGTH:
                return self._handle_wait_length(byte)
            case DeserializerState.WAIT_PAYLOAD:
                return self._handle_wait_payload(byte)
            case DeserializerState.WAIT_CHECKSUM:
                return self._handle_wait_checksum(byte)

        self._reset()
        return None

    def _handle_wait_header_1(self, byte: int) -> None:
        if byte == self.HEADER_BYTE:
            self._buffer.clear()
            self._buffer.append(byte)
            self._state = DeserializerState.WAIT_HEADER_2
        return None

    def _handle_wait_header_2(self, byte: int) -> None:
        if byte == self.HEADER_BYTE:
            self._buffer.append(byte)
            self._state = DeserializerState.WAIT_ID
        else:
            self._state = DeserializerState.WAIT_HEADER_1
        return None

    def _handle_wait_id(self, byte: int) -> None:
        self._buffer.append(byte)
        self._state = DeserializerState.WAIT_LENGTH
        return None

    def _handle_wait_length(self, byte: int) -> None:
        if byte < 2 or byte > self.MAX_FRAME_LENGTH:
            self._reset()
            return None

        self._buffer.append(byte)
        self._remaining_payload = byte - 1  # instruction + params
        self._state = DeserializerState.WAIT_PAYLOAD
        return None

    def _handle_wait_payload(self, byte: int) -> None:
        self._buffer.append(byte)
        self._remaining_payload -= 1

        if self._remaining_payload < 0:
            self._reset()
            return None

        if self._remaining_payload == 0:
            self._state = DeserializerState.WAIT_CHECKSUM
        return None

    def _handle_wait_checksum(self, byte: int) -> Optional["ServoPacket"]:
        self._buffer.append(byte)

        frame = bytes(self._buffer)
        self._reset()

        if not self._validate_checksum(frame):
            return None

        return self._build_packet(frame)

    def _reset(self):
        self._state = DeserializerState.WAIT_HEADER_1
        self._buffer.clear()
        self._remaining_payload = 0

    @staticmethod
    def _validate_checksum(frame: bytes) -> bool:
        data = frame[2:-1]
        received = frame[-1]
        calculated = (~sum(data)) & 0xFF
        return received == calculated

    @staticmethod
    def _build_packet(frame: bytes) -> "ServoPacket":
        return ServoPacket(
            servo_id=frame[2],
            instruction=frame[4],
            params=list(frame[5:-1]),
        )
