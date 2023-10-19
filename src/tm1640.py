from adafruit_bus_device.spi_device import SPIDevice
from micropython import const
import digitalio
import time

# Display commands
_CMD_DSP = const(0b10_000000)
_CMD_DSP_DISPLAY_ON = const(0b1000_1000)
_CMD_DSP_DISPLAY_OFF = const(0b1000_0000)

# Address command
_CMD_ADDR = const(0b1100_0000)

# Data commands
_CMD_DATA = const(0b0100_0000)
_CMD_DATA_AUTO = const(0b0100_0000)
_CMD_DATA_FIXED = const(0b0100_0100)

#: The valid bits when using an int for a frame
FRAME_MASK = 0xFF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF


class TM1640:
    def __init__(self, clock, data):
        self.clock = digitalio.DigitalInOut(clock)
        self.data = digitalio.DigitalInOut(data)

        self.clock.switch_to_output(True)
        self.data.switch_to_output(True)

        # Max is one command byte followed by 16 data bytes
        self._buf = bytearray(17)

        self._init_display()

    def _send(self, length):
        # 1. Set Clock low
        self.data.value = False
        self.clock.value = False

        # 2. Send data
        for byte in self._buf[:length]:
            for _ in range(8):
                self.data.value = byte & 1
                self.clock.value = True
                time.sleep(6 / 1_000_000)
                self.clock.value = False
                byte >>= 1

        # Set clock high
        self.clock.value = True
        self.data.value = True

    def _init_display(self):
        """
        Set up the display
        """
        # Put us in auto mode
        self._buf[0] = _CMD_DATA_AUTO
        self._send(1)

    def display_on(self, brightness):
        """
        Turn on the display and set the brightness
        """
        assert 0 <= brightness < 8
        self._buf[0] = _CMD_DSP_DISPLAY_ON | brightness
        self._send(1)

    def display_off(self):
        """
        Turn off the display
        """
        self._buf[0] = _CMD_DSP_DISPLAY_OFF
        self._send(1)

    def set_data_seq(self, addr, data):
        """
        Send the given frame to the display. Data is a sequence of bytes.
        """
        assert 0 <= addr < 0x10
        self._buf[0] = _CMD_ADDR | addr
        self._buf[1:len(data) + 1] = data
        self._send(len(data) + 1)

    def set_data_int(self, addr, data):
        """
        Send the given frame to the display. Data is an int, interpreted as little endian
        """
        assert 0 <= addr < 0x10
        self._buf[0] = _CMD_ADDR | addr
        self._buf[1:17] = data.to_bytes(16, 'little')
        self._send(17)
