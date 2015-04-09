# -*- coding: utf-8 -*-

class SpriteMemory(object):

    def __init__(self):
        self._memory = []

    def read_data(self, addr):
        return self._memory[addr]

    def write_data(self, data, addr):
        a = addr & 0xFF
        d = data & 0xFF
        self._memory[a] = d