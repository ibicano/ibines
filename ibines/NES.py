# -*- coding: utf-8 -*-


from ROM import ROM
from PPU import PPU
from CPU import CPU
from Memory import Memory
from Instruction import *



class NES(object):

    def __init__(self, file_name):
        self._rom = ROM(file_name)
        self._ppu = PPU()
        self._memory = Memory(self._ppu, self._rom)
        self._cpu = CPU()


    ###########################################################################
    # Variables privadas
    ###########################################################################

    _rom = None
    _ppu = None
    # Referencia al sistema de memoria
    _memory = None
    # Referencia a la CPU
    _cpu = None
