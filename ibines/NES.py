# -*- coding: utf-8 -*-


from ROM import ROM
from PPU import PPU
from CPU import CPU
from Memory import Memory
from Instruction import *



class NES(object):

    def __init__(self, file_name):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._rom = ROM(file_name)
        self._ppu = PPU()
        self._memory = Memory(self._ppu, self._rom)
        self._cpu = CPU()
        #######################################################################
        #######################################################################
