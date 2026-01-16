from dataclasses import dataclass
from typing import Optional, List
import time

from transport.serial import SerialTransport
from protocol.serializer import PacketSerializer
from protocol.deserializer import PacketDeserializer
from protocol.protocol import ServoProtocol, ServoPacket
from protocol.packet_decoder import PacketDecoder


class ServoTimeoutError(Exception):
    pass


class ServoResponseError(Exception):
    pass


@dataclass(frozen=True)
class ServoStatus:
    servo_id: int
    error: int
    params: List[int]


class ServoBusDriver:
    def __init__(
        self,
        port: str,
        baudrate: int,
        *,
        transport: Optional[SerialTransport] = None,
        protocol: Optional[ServoProtocol] = None,
        serializer: Optional[PacketSerializer] = None,
        deserializer: Optional[PacketDeserializer] = None,
    ):
        self.transport = transport or SerialTransport(port=port, baudrate=baudrate)
        self.protocol = protocol or ServoProtocol()
        self.serializer = serializer or PacketSerializer()
        self.deserializer = deserializer or PacketDeserializer()
        self._decoder = PacketDecoder()

    def connect(self):
        self.transport.open()

    def disconnect(self):
        self.transport.close()

    def execute(self, packet: ServoPacket, timeout: float):
        raw = self.serializer.serialize(packet)
        self.transport.send(raw)

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            data = self.transport.receive(64)
            if not data:
                continue

            packets = self.deserializer.feed(data)
            for rx in packets:
                if rx.servo_id == packet.servo_id:
                    return rx

        raise ServoTimeoutError("No response from servo")

    def go_to_position(
        self,
        servo_id: int,
        position: int,
        *,
        speed: int = 1000,
        acc: int = 50,
        timeout: float = 0.2,
    ):
        pkt = self.protocol.move_absolute(
            servo_id,
            position=position,
            speed=speed,
            acc=acc,
        )
        return self.execute(pkt, timeout)

    def go_continues(
        self, servo_id: int, *, speed: int, acc: int, timeout: float = 0.2
    ):
        pkt = self.protocol

    def get_position(self, servo_id: int):
        return self._read_and_decode(
            request=self.protocol.read_position(servo_id=servo_id),
            decode_fn=self._decoder.position,
        )

    def get_speed(self, servo_id: int):
        return self._read_and_decode(
            request=self.protocol.read_speed(servo_id=servo_id),
            decode_fn=self._decoder.speed,
        )

    def get_temperature(self, servo_id: int):
        return self._read_and_decode(
            request=self.protocol.read_temperature(servo_id),
            decode_fn=self._decoder.temperature,
        )

    def get_voltage(self, servo_id: int):
        return self._read_and_decode(
            request=self.protocol.read_voltage(servo_id),
            decode_fn=self._decoder.voltage,
        )

    def get_load(self, servo_id: int):
        return self._read_and_decode(
            request=self.protocol.read_load(servo_id), decode_fn=self._decoder.load
        )

    def get_current(self, servo_id: int):
        return self._read_and_decode(
            request=self.protocol.read_current(servo_id),
            decode_fn=self._decoder.current,
        )

    def _read_and_decode(self, request, decode_fn, timeout: float = 0.2):
        packet = self.execute(request, timeout)
        return decode_fn(packet)
