# -*- coding: utf-8 -*-

import Mapper

"""
Memory

Descripción: Implementa la Memoria del sistema
"""
class Memory(object):

    SIZE = 0x10000

    # Constructor
    # Se le pasa una instancia de la PPU y otra de la ROM para el mapeo en memoria de ambos
    def __init__(self, ppu, mapper, joypad_1):
        #######################################################################
        # Variables de instancia
        #######################################################################

        # Array para almacenar el contenido de la memoria
        self._memory = [0x00] * Memory.SIZE
        self._joypad_1 = joypad_1
        self._ppu = ppu
        self._mapper = mapper

        #######################################################################
        #######################################################################


    # Devuelve el contenido de una posición de memoria
    def read_data(self, addr):
        d = 0x00
        if addr >= 0x8000:    # Lee del mapper de la ROM
            d = self._mapper.read_prg(addr)
        elif addr >= 0x0000 and addr < 0x2000:
            d = self._memory[addr]
        elif addr >= 0x2000 and addr < 0x4000:     # Direcciones de los registros PPU
            d = self._ppu.read_reg(0x2000 + (addr & 0x07))
        elif addr >= 0x4000 and addr < 0x4020:
            if addr == 0x4016:
                d = self._joypad_1.read_reg()
            elif addr == 0x4017:
                pass
        elif 0x6000 <= addr <= 0x7FFF:
            d = self._memory[addr]

        return d


    # TODO: acabar esta función
    # Establece el contenido de una posición de memoria
    # Se escribe en todas las posiciones de las que se hace mirror. Sería más
    # eficiente no escribir todas y mapear las posiciones en una soloa
    # OPTIMIZE: Lo expuesto anteriormente
    def write_data(self, data, addr):
        d = data & 0xFF
        addr = addr & 0xFFFF

        if addr >= 0x0000 and addr < 0x2000:
            n = addr % 0x800
            self._memory[n] = d
            self._memory[0x0800 + n] = d
            self._memory[0x1000 + n] = d
            self._memory[0x1800 + n] = d
        elif addr >= 0x2000 and addr < 0x4000: # Direcciones de los registros PPU
            n = 0x2000 + (addr & 0x07)
            self._ppu.write_reg(d, n)
        elif addr >= 0x4000 and addr <= 0x401F: # Más registros I/O
            if addr == 0x4014:
                self._ppu.write_sprite_dma(self, d)
            elif addr == 0x4016:
                self._joypad_1.write_reg(d)
            elif addr == 0x4017:
                pass
        elif 0x6000 <= addr <= 0x7FFF:
            self._memory[addr] = d
        elif addr >= 0x8000:
            self._mapper.write_prg(d, addr)
