import logging
from protocol.deserializer import PacketDeserializer

_LOGGER = logging.getLogger(__name__)


def test_minimum_valid_frame():
    frame = b"\xff\xff\x01\x02\x00\xfc"
    deserializer = PacketDeserializer()

    packets = deserializer.feed(frame)

    _LOGGER.debug(packets)

    assert len(packets) == 1
    assert packets[0].servo_id == 1
    assert packets[0].instruction == 0x00
    assert packets[0].params == []


def test_valid_frame_with_parameters():
    """Test for a frame with parameters."""
    pass


def test_invalid_header():
    """Test for a frame with an invalid header."""
    pass


def test_invalid_checksum():
    """Test for a frame with an invalid checksum."""
    pass


def test_incomplete_frame():
    """Test for incomplete frames."""
    pass


def test_valid_checksum_calculation():
    """Test the checksum calculation for known data."""
    pass


def test_invalid_frame_length():
    """Test a frame indicating a wrong length larger than the buffer size."""
    pass


def test_parse_with_extra_bytes():
    """Test for a frame with extra bytes after the frame."""
    pass


def test_empty_buffer():
    """Test for parsing an empty buffer."""
    pass


def test_edge_case_frame_length_zero():
    """Test for valid frame with a LENGTH field of 0."""
    pass
