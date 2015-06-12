# -*- coding: utf-8 -*-

import Mapper

###############################################################################
# Clase: NES
# Descripción: Implementa la memoria principal de la NES
###############################################################################
class Memory(object):

    SIZE = 0x10000

    # Constructor
    # Se le pasa una instancia de la PPU y otra de la ROM para el mapeo en memoria de ambos
    def __init__(self, ppu, mapper, joypad_1):
        # Array para almacenar el contenido de la memoria
        self._memory = [0x00] * Memory.SIZE
        self._joypad_1 = joypad_1
        self._ppu = ppu
        self._mapper = mapper


    ###############################################################################
    # Función: read(addr)
    # Parámetros:
    #   addr -> dirección de memoria a leer (16 bits)
    # Descripción: Lee la posición de memoria indicada por el parámetro 'addr', que
    # tiene que se un número de 16 bits, y devuelve el contenido
    ###############################################################################
    def read_data(self, addr):
        d = 0x00
        if addr >= 0x8000:      # Memoria del programa. Lee del mapper de la ROM
            d = self._mapper.read_prg(addr)
        elif addr >= 0x0000 and addr < 0x2000:      # Memoria RAM
            d = self._memory[addr]
        elif addr >= 0x2000 and addr < 0x4000:     # Direcciones de los registros PPU
            d = self._ppu.read_reg(0x2000 + (addr & 0x07))
        elif addr >= 0x4000 and addr < 0x4020:      # Más registros I/O
            if addr == 0x4016:      # Registro del Joypad 1
                d = self._joypad_1.read_reg()
            elif addr == 0x4017:        # Registro del Joypad 2
                pass
        elif 0x6000 <= addr <= 0x7FFF:      # Memoria de estado de la partida.
            d = self._memory[addr]

        return d


    ###############################################################################
    # Función: write(data, addr)
    # Parámetros:
    #   data -> dato a escribir en memoria (8 bits)
    #   addr -> dirección de memoria a escribir (16 bits)
    # Descripción: Escribe el dato 'data' en la posición de memoria 'addr'
    ###############################################################################
    def write_data(self, data, addr):
        d = data & 0xFF
        addr = addr & 0xFFFF

        if addr >= 0x0000 and addr < 0x2000:        # Espacio de memoria RAM
            n = addr % 0x800
            self._memory[n] = d
            self._memory[0x0800 + n] = d
            self._memory[0x1000 + n] = d
            self._memory[0x1800 + n] = d
        elif addr >= 0x2000 and addr < 0x4000:      # Direcciones de los registros PPU
            n = 0x2000 + (addr & 0x07)
            self._ppu.write_reg(d, n)
        elif addr >= 0x4000 and addr <= 0x401F:     # Más registros I/O
            if addr == 0x4014:      # Escritura de memoria de Sprites por DMA
                self._ppu.write_sprite_dma(self, d)
            elif addr == 0x4016:        # Joypad 1
                self._joypad_1.write_reg(d)
            elif addr == 0x4017:        # Joypad 2
                pass
        elif 0x6000 <= addr <= 0x7FFF:
            self._memory[addr] = d
        elif addr >= 0x8000:            # Memoria de programa. Escribe al mapper.
            self._mapper.write_prg(d, addr)
