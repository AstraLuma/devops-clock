
SEVEN_SEGMENTS = {
    0: 0b0011_1111,
    1: 0b0000_0110,
    2: 0b0101_1011,
    3: 0b0100_1111,
    4: 0b0110_0110,
    5: 0b0110_1101,
    6: 0b0111_1101,
    7: 0b0000_0111,
    8: 0b0111_1111,
    9: 0b0110_1111,
}

COLON = 0x00_00_00_00_00_00_00_00_00_00_00_00_00_80_80_00
SLASH = 0x00_00_00_00_10_20_00_00_00_00_00_00_00_00_00_00


def num2digit(pos, numeral):
    return SEVEN_SEGMENTS[numeral] << (pos * 8)


def render_time(hours, minutes):
    frame = COLON
    frame |= num2digit(3, minutes % 10)
    frame |= num2digit(2, minutes // 10)
    frame |= num2digit(1, hours % 10)
    frame |= num2digit(0, hours // 10)
    return frame


def render_date(day, month):
    frame = SLASH
    frame |= num2digit(7, day % 10)
    frame |= num2digit(6, day // 10)
    frame |= num2digit(5, month % 10)
    frame |= num2digit(4, month // 10)
    return frame


def render_timestamp(time):
    frame = 0
    frame |= render_time(time.tm_hour, time.tm_min)
    frame |= render_date(time.tm_mday, time.tm_mon)
    return frame
