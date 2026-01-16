from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol.protocol import ServoPacket


class PacketDecoder:
    """
    Decode ServoPacket payload into typed values.
    """

    @staticmethod
    def u8(packet: "ServoPacket") -> int:
        PacketDecoder._require_len(packet, 1)
        return packet.params[0]

    @staticmethod
    def u16(packet: "ServoPacket") -> int:
        PacketDecoder._require_len(packet, 2)
        return packet.params[0] | (packet.params[1] << 8)

    @staticmethod
    def s16(packet: "ServoPacket") -> int:
        raw = PacketDecoder.u16(packet)
        if raw & 0x8000:
            return -(raw & 0x7FFF)
        return raw

    @staticmethod
    def position(packet: "ServoPacket") -> int:
        return PacketDecoder.u16(packet)

    @staticmethod
    def speed(packet: "ServoPacket") -> int:
        return PacketDecoder.s16(packet)

    @staticmethod
    def current(packet: "ServoPacket") -> int:
        return PacketDecoder.s16(packet)

    @staticmethod
    def load(packet: "ServoPacket") -> int:
        return PacketDecoder.s16(packet)

    @staticmethod
    def voltage(packet: "ServoPacket") -> float:
        return PacketDecoder.u8(packet) / 10.0

    @staticmethod
    def temperature(packet: "ServoPacket") -> int:
        return PacketDecoder.u8(packet)

    @staticmethod
    def _require_len(packet: "ServoPacket", expected: int):
        if len(packet.params) != expected:
            raise ValueError(
                f"Invalid payload length: expected {expected}, got {len(packet.params)}"
            )
