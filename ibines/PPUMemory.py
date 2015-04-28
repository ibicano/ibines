# -*- coding: utf-8 -*-

"""
PPUMemory

Descripción: Implementa la Memoria del procesador gráfico
"""
class PPUMemory(object):
    # Constantes
    ADDR_PATTERN_0 = 0x0000
    ADDR_PATTERN_1 = 0x1000

    ADDR_NAME_0 = 0x2000
    ADDR_ATTR_0 = 0x23C0
    ADDR_NAME_1 = 0x2400
    ADDR_ATTR_1 = 0x27C0
    ADDR_NAME_2 = 0x2800
    ADDR_ATTR_2 = 0x2BC0
    ADDR_NAME_3 = 0x2C00
    ADDR_ATTR_3 = 0x2FC0

    ADDR_IMAGE_PALETTE = 0x3F00
    ADDR_SPRITE_PALETTE = 0x3F10


    def __init__(self, ppu, rom):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._memory = [0x00] * 0x10000

        # Referencia a la PPU
        self._ppu = ppu

        # Referencia a la ROM
        self._rom = rom
        if self._rom.get_chr_count() == 1:
            self._memory[0x0000:0x2000] = self._rom.get_chr()

        self._mirror_mode = rom.get_mirroring()        # Modo de mirror de los "name tables" (sacado de la ROM). 0: horizontal, 1: vertical
        #######################################################################
        #######################################################################


    #Lee un dato de la memoria de la PPU:
    def read_data(self, addr):
        a = addr & 0xFFFF
        d = 0x00

        d = self._memory[a]

        return d


    # TODO: implementar los mirrors a partir de la 0x4000
    # Escribe un dato en la memoria de la PPU
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF

        # Name tables y attribute tables:
        if a < 0x4000:
            if a >= 0x2000 and a < 0x2400:
                if self._mirror_mode == 0:
                    self._set_memory(d, a + 0x0400)
                    self._set_memory(d, a + 0x1400)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a + 0x0800)
                    self._set_memory(d, a + 0x1800)
            elif a >= 0x2400 and a < 0x2800:
                if self._mirror_mode == 0:
                    self._set_memory(d, a - 0x0400)
                    self._set_memory(d, a - 0x1400)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a + 0x0800)
                    self._set_memory(d, a + 0x1800)
            elif a >= 0x2800 and a < 0x2C00:
                if self._mirror_mode == 0:
                    self._set_memory(d, a + 0x0400)
                    self._set_memory(d, a + 0x1400)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a - 0x0800)
                    self._set_memory(d, a - 0x1800)
            elif a >= 0x2C00 and a < 0x3000:
                if self._mirror_mode == 0:
                    self._set_memory(d, a - 0x0400)
                    if a < 0x2F00: self._set_memory(d, a - 0x1400)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a - 0x0800)
                    if a < 0x2F00: self._set_memory(d, a - 0x1800)
            # Mirrors Name Tables y Attr Tables
            elif a >= 0x3000 and a < 0x3F00:
                self.write_data(d, a - 0x1000)
            # Paletas
            elif a >= 0x3F00 and a < 0x3F20:
                # El elemento inicial de la paleta se repite cada 4, por lo que se duplica si una posición es 0 modulo 4
                if (a - 0x3F00) % 4 == 0:
                    for x in range(0x3F00, 0x4000, 0x04):
                        self._set_memory(d, x)
                # Escribe en mirrors
                self._set_memory(d, a + 0x0020)
                self._set_memory(d, a + 0x0040)
                self._set_memory(d, a + 0x0060)
                self._set_memory(d, a + 0x0080)
                self._set_memory(d, a + 0x00A0)
                self._set_memory(d, a + 0x00C0)
                self._set_memory(d, a + 0x00E0)
            # Mirrors paletas
            elif a >= 0x3F20 and a < 0x4000:
                self.write_data(d, ((a - 0x3F20) % 0x0020) + 0x3F00)

            # Escribimos en la posición indicada
            self._set_memory(d, a)
        # Mirrors generales
        elif a >= 0x4000:
            self.write_data(d, (a - 0x4000) % 0x4000)


    # Funciones de ayuda
    # Devuelve un patrón de la pattern table
    def read_pattern(self, table, pattern_number):
        addr = pattern_number * 0x0010
        pattern = []
        if table == 0:
            pattern = self._memory[addr:addr + 16]
        elif table == 1:
            addr = addr + 0x1000
            pattern = self._memory[addr:addr + 16]

        return pattern


    # Establece el valor de una posición de memoria con los mirrors
    def _set_memory(self, d, addr):
        a = addr % 0x4000
        self._memory[a] = d
        self._memory[a + 0x4000] = d
        self._memory[a + 0x8000] = d
        self._memory[a + 0xC000] = d

