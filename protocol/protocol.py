import enum
from dataclasses import dataclass
from typing import List


@dataclass
class ServoPacket:
    servo_id: int
    instruction: int
    params: List[int]


class Instruction(enum.IntEnum):
    PING = 1
    READ = 2
    WRITE = 3
    REG_WRITE = 4
    ACTION = 5


class SCSRegister(enum.IntEnum):
    # -------------------------
    # EPROM (read-only)
    # -------------------------
    MODEL_L = 3
    MODEL_H = 4

    # -------------------------
    # EPROM (read/write)
    ID = 5
    BAUD_RATE = 6
    MIN_ANGLE_LIMIT_L = 9
    MIN_ANGLE_LIMIT_H = 10
    MAX_ANGLE_LIMIT_L = 11
    MAX_ANGLE_LIMIT_H = 12
    CW_DEAD = 26
    CCW_DEAD = 27
    OFS_L = 31
    OFS_H = 32
    CONTINUE_MODE = 33

    # SRAM (read/write)
    TORQUE_ENABLE = 40
    GOAL_ACC = 41
    GOAL_POSITION_L = 42
    GOAL_POSITION_H = 43
    GOAL_TIME_L = 44
    GOAL_TIME_H = 45
    GOAL_SPEED_L = 46
    GOAL_SPEED_H = 47
    LOCK = 48

    # SRAM (read-only)
    PRESENT_POSITION_L = 56
    PRESENT_POSITION_H = 57
    PRESENT_SPEED_L = 58
    PRESENT_SPEED_H = 59
    PRESENT_LOAD_L = 60
    PRESENT_LOAD_H = 61
    PRESENT_VOLTAGE = 62
    PRESENT_TEMPERATURE = 63
    MOVING = 66
    PRESENT_CURRENT_L = 69
    PRESENT_CURRENT_H = 70


class ServoProtocol:

    def read_position(self, servo_id: int) -> ServoPacket:
        return self.read(
            servo_id,
            SCSRegister.PRESENT_POSITION_L,
            2,
        )

    def read_speed(self, servo_id: int) -> ServoPacket:
        return self.read(
            servo_id,
            SCSRegister.PRESENT_SPEED_L,
            2,
        )

    def read_load(self, servo_id: int) -> ServoPacket:
        return self.read(
            servo_id,
            SCSRegister.PRESENT_LOAD_L,
            2,
        )

    def read_voltage(self, servo_id: int) -> ServoPacket:
        return self.read(
            servo_id,
            SCSRegister.PRESENT_VOLTAGE,
            1,
        )

    def read_temperature(self, servo_id: int) -> ServoPacket:
        return self.read(
            servo_id,
            SCSRegister.PRESENT_TEMPERATURE,
            1,
        )

    def read_current(self, servo_id: int) -> ServoPacket:
        return self.read(
            servo_id,
            SCSRegister.PRESENT_CURRENT_L,
            2,
        )

    def write_absolute_move(
        self,
        servo_id: int,
        position: int,
        *,
        speed: int,
        acc: int,
    ) -> ServoPacket:
        if not (0 <= position <= 4095):
            raise ValueError("Position must be in range 0..4095")

        params = [
            acc & 0xFF,
            position & 0xFF,
            (position >> 8) & 0xFF,
            0x00,
            0x00,
            speed & 0xFF,
            (speed >> 8) & 0xFF,
        ]

        return self.write(
            servo_id,
            SCSRegister.GOAL_ACC,
            params,
        )

    def write_continues_move(
        self,
        servo_id: int,
        *,
        speed: int,
        acc: int,
    ) -> ServoPacket:

        params = [
            acc & 0xFF,
            0x00,
            0x00,
            0x00,
            0x00,
            speed & 0xFF,
            (speed >> 8) & 0xFF,
        ]

        return self.write(
            servo_id,
            SCSRegister.GOAL_ACC,
            params,
        )

    @classmethod
    def ping(cls, servo_id: int) -> ServoPacket:
        return ServoPacket(
            servo_id=servo_id,
            instruction=int(Instruction.PING),
            params=[],
        )

    @classmethod
    def read(cls, servo_id: int, address: int, size: int) -> ServoPacket:
        return ServoPacket(
            servo_id=servo_id,
            instruction=int(Instruction.READ),
            params=[address & 0xFF, size & 0xFF],
        )

    @classmethod
    def write(cls, servo_id: int, address: int, data: List[int]) -> ServoPacket:
        return ServoPacket(
            servo_id=servo_id,
            instruction=int(Instruction.WRITE),
            params=[address & 0xFF] + [b & 0xFF for b in data],
        )
