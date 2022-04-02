def calc_crc(frame):
    return (sum(frame[2:-1]) & 0xff) ^ 0x44


def calc_crc_for_payload(payload):
    return (sum(payload) & 0xff) ^ 0x44


def verify_crc(packet):
    assert len(packet) == 36

    crc = (sum(packet[2:-1]) & 0xff) ^ 0x44
    valid_crc = packet[-1]

    if crc != valid_crc:
        raise Exception("invalid crc")
