"""
Library to store state in NVM.

This should be values that aren't really meaningful to the user,
but we want to cache over power cycles.
"""
import microcontroller
import struct


class NVState:
    version: int = 1
    tz_offset: int = 0

    __struct = '@Bl'
    __unpacking = False

    def __init__(self):
        self.__size = struct.calcsize(self.__struct)
        self._unpack()

    def _unpack(self):
        data = struct.unpack(self.__struct, microcontroller.nvm[:self.__size])
        self.__unpacking = True
        if data[0] == 1:
            self.version, self.tz_offset = data
        self.__unpacking = False

    def _pack(self):
        microcontroller.nvm[:self.__size] = struct.pack(
            self.__struct,
            self.version, self.tz_offset
        )

    def __setattr__(self, name, value):
        old = getattr(self, name)
        super().__setattr__(name, value)
        if not self.__unpacking and old != value:
            self._pack()
