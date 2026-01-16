from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .protocol import ServoPacket


class ServoSerializationError(Exception):
    pass


class PacketSerializer:
    HEADER = b"\xff\xff"

    MAX_FRAME_LENGTH = 64
    MAX_PARAMS_LENGTH = 60

    def serialize(self, packet: "ServoPacket") -> bytes:
        self._validate_packet(packet)

        frame = bytearray()

        self._append_header(frame)
        self._append_servo_id(frame, packet.servo_id)
        self._append_length(frame, packet)
        self._append_instruction(frame, packet.instruction)
        self._append_params(frame, packet.params)
        self._append_checksum(frame)

        return bytes(frame)

    def _append_header(self, frame: bytearray):
        frame += self.HEADER

    def _append_servo_id(self, frame: bytearray, servo_id: int):
        frame.append(servo_id & 0xFF)

    def _append_length(self, frame: bytearray, packet: "ServoPacket"):
        length = self._calculate_length(packet)
        frame.append(length)

    def _append_instruction(self, frame: bytearray, instruction: int):
        frame.append(instruction & 0xFF)

    def _append_params(self, frame: bytearray, params: List[int]):
        for p in params:
            frame.append(p & 0xFF)

    def _append_checksum(self, frame: bytearray):
        checksum = self._calculate_checksum(frame[2:])
        frame.append(checksum)

    def _validate_packet(self, packet: "ServoPacket"):
        self._validate_servo_id(packet.servo_id)
        self._validate_instruction(packet.instruction)
        self._validate_params(packet.params)
        self._validate_length(packet)

    def _validate_servo_id(self, servo_id: int):
        if not (0 <= servo_id <= 0xFE):
            raise ServoSerializationError("Invalid servo_id")

    def _validate_instruction(self, instruction: int):
        if not (0 <= instruction <= 0xFF):
            raise ServoSerializationError("Invalid instruction")

    def _validate_params(self, params: List[int]):
        if len(params) > self.MAX_PARAMS_LENGTH:
            raise ServoSerializationError("Too many params")

        for p in params:
            if not (0 <= p <= 0xFF):
                raise ServoSerializationError("Param out of range")

    def _validate_length(self, packet: "ServoPacket"):
        length = self._calculate_length(packet)

        if length < 2:
            raise ServoSerializationError("Frame too short")

        if length > self.MAX_FRAME_LENGTH:
            raise ServoSerializationError("Frame too long")

    def _calculate_length(self, packet: "ServoPacket") -> int:
        # instruction + params + checksum
        return 1 + len(packet.params) + 1

    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        return (~sum(data)) & 0xFF
