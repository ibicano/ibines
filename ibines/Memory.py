# -*- coding: utf-8 -*-

"""
Memory

Descripción: Implementa la Memoria del sistema
"""
class Memory(object):

    # Constructor
    # Se le pasa una instancia de la PPU y otra de la ROM para el mapeo en memoria de ambos
    def __init__(self, ppu, rom):
        #######################################################################
        # Variables de instancia
        #######################################################################

        # Array para almacenar el contenido de la memoria
        self._memory = []
        self._ppu = ppu
        self._rom = rom
        #######################################################################
        #######################################################################


    # TODO: acabar esta función
    # Devuelve el contenido de una posición de memoria
    def read_data(self, addr):
        a = addr & 0xFFFF

        d = 0x00
        if a >= 0x0000 and a <= 0x1FFF:
            d = self._memory[a]
        elif a >= 0x2000 and a <= 0x3FFF:     # Direcciones de los registros PPU
            n = 0x2000 + (a % 0x08)
            d = self._ppu.read_reg(n)
        elif a >= 0x8000 and a <= 0xFFFF:    # Lee la ROM
            d = self._rom.read_pgr_data(a % 0x8000)

        return d


    # TODO: acabar esta función
    # Establece el contenido de una posición de memoria
    # Se escribe en todas las posiciones de las que se hace mirror. Sería más
    # eficiente no escribir todas y mapear las posiciones en una soloa
    # OPTIMIZE: Lo expuesto anteriormente
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF

        if a >= 0x0000 and a <= 0x1FFF:
            n = 0x2000 + (a % 0x800)
            self._memory[n] = d
            self._memory[0x0800 + n] = d
            self._memory[0x1000 + n] = d
            self._memory[0x1800 + n] = d
        elif a >= 0x2000 and a <= 0x3FFF: # Direcciones de los registros PPU
            n = a % 0x08
            self._ppu.write_reg(d, n)
        elif a >= 0x4000 and a <= 0x401F: # Más registros I/O
            if a == 0x4014:
                self._ppu.write_sprite_dma(self, d)
