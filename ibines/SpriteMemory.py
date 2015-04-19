# -*- coding: utf-8 -*-

class SpriteMemory(object):

    SIZE = 256

    def __init__(self):
        self._memory = [0x00] * SpriteMemory.SIZE

    def read_data(self, addr):
        return self._memory[addr]

    def write_data(self, data, addr):
        a = addr & 0xFF
        d = data & 0xFF
        self._memory[a] = d