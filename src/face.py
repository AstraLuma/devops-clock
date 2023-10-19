
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

DAYS_OF_WEEK = {
    0: 0x00_00_26_13_46_51_07_13_00_00_00_00_00_00_00_00,  # MON
    1: 0x00_00_48_59_46_11_10_44_00_00_00_00_00_00_00_00,  # TUE
    2: 0x00_00_56_44_48_59_26_31_00_00_00_00_00_00_00_00,  # WED
    3: 0x00_00_46_11_0E_19_10_44_00_00_00_00_00_00_00_00,  # THU
    4: 0x00_00_50_44_2A_59_00_59_00_00_00_00_00_00_00_00,  # FRI
    5: 0x00_00_10_44_0E_59_4C_49_00_00_00_00_00_00_00_00,  # SAT
    6: 0x00_00_26_13_46_11_4C_49_00_00_00_00_00_00_00_00,  # SUN
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


def render_dow(day):
    return DAYS_OF_WEEK[day]


def render_timestamp(time):
    frame = 0
    frame |= render_time(time.tm_hour, time.tm_min)
    frame |= render_date(time.tm_mday, time.tm_mon)
    frame |= render_dow(time.tm_wday)
    return frame
