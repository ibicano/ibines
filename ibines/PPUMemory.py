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

        d = self._memory[a]

        return d


    # Escribe un dato en la memoria de la PPU
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF

        # Name tables y attribute tables:
        if 0x2000 <= a < 0x4000:
            # Name Table 0
            if a >= 0x2000 and a < 0x2400:
                if self._mirror_mode == 0:
                    self._set_memory(d, a + 0x0400)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x1400)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a + 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x1800)
            # Name Table 1
            elif a >= 0x2400 and a < 0x2800:
                if self._mirror_mode == 0:
                    self._set_memory(d, a - 0x0400)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0C00)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a + 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    if a < 0x2700:
                        self._set_memory(d, a + 0x1800)
            # Name Table 2
            elif a >= 0x2800 and a < 0x2C00:
                if self._mirror_mode == 0:
                    self._set_memory(d, a + 0x0400)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    if a < 0x2B00:
                        self._set_memory(d, a + 0x1400)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a - 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0800)
            # Name Table 3
            elif a >= 0x2C00 and a < 0x3000:
                if self._mirror_mode == 0:
                    self._set_memory(d, a - 0x0400)
                    # Mirrors
                    if a < 0x2F00:
                        self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0C00)
                elif self._mirror_mode == 1:
                    self._set_memory(d, a - 0x0800)
                    # Mirrors
                    if a < 0x2F00:
                        self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0800)
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
            self.write_data(d, a % 0x4000)


    # Funciones de ayuda

    # Establece el valor de una posición de memoria con los mirrors
    def _set_memory(self, d, addr):
        a = addr % 0x4000
        self._memory[a] = d
        self._memory[a + 0x4000] = d
        self._memory[a + 0x8000] = d
        self._memory[a + 0xC000] = d

