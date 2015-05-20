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


    def __init__(self, ppu, mapper):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._memory = [0x00] * 0x10000

        # Referencia a la PPU
        self._ppu = ppu

        self._mapper = mapper
        #######################################################################
        #######################################################################


    #Lee un dato de la memoria de la PPU:
    def read_data(self, addr):
        a = addr & 0xFFFF
        d = 0x00

        if (a & 0x2000):
            d = self._memory[a]
        else:
            d = self._mapper.read_chr(a)

        return d


    # Escribe un dato en la memoria de la PPU
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF

        # Pattern tables:
        if (0x0000 <= a <= 0x1FFF) and self._mapper.get_chr_count() == 0:
            self._mapper.write_chr(d, a)
        # Name tables y attribute tables:
        elif 0x2000 <= a < 0x4000:
            # Name Table 0
            if 0x2000 <= a < 0x2400:
                if self._mapper.mirror_mode() == 0:
                    self._set_memory(d, a + 0x0400)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x1400)
                elif self._mapper.mirror_mode() == 1:
                    self._set_memory(d, a + 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x1800)
                elif self._mapper.mirror_mode() == 2:
                    self._set_memory(d, a + 0x0400)
                    self._set_memory(d, a + 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x1400)
                    self._set_memory(d, a + 0x1800)

                # Escribimos en la posición indicada
                self._set_memory(d, a)
            # Name Table 1
            elif 0x2400 <= a < 0x2800:
                if self._mapper.mirror_mode() == 0:
                    self._set_memory(d, a - 0x0400)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0C00)
                elif self._mapper.mirror_mode() == 1:
                    self._set_memory(d, a + 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    if a < 0x2700:
                        self._set_memory(d, a + 0x1800)
                elif self._mapper.mirror_mode() == 2:
                    self._set_memory(d, a - 0x0400)
                    self._set_memory(d, a + 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0C00)
                    if a < 0x2700:
                        self._set_memory(d, a + 0x1800)

                # Escribimos en la posición indicada
                self._set_memory(d, a)
            # Name Table 2
            elif 0x2800 <= a < 0x2C00:
                if self._mapper.mirror_mode() == 0:
                    self._set_memory(d, a + 0x0400)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    if a < 0x2B00:
                        self._set_memory(d, a + 0x1400)
                elif self._mapper.mirror_mode() == 1:
                    self._set_memory(d, a - 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0800)
                elif self._mapper.mirror_mode() == 2:
                    self._set_memory(d, a + 0x0400)
                    self._set_memory(d, a - 0x0800)
                    # Mirrors
                    self._set_memory(d, a + 0x1000)
                    if a < 0x2B00:
                        self._set_memory(d, a + 0x1400)
                    self._set_memory(d, a + 0x0800)

                # Escribimos en la posición indicada
                self._set_memory(d, a)
            # Name Table 3
            elif 0x2C00 <= a < 0x3000:
                if self._mapper.mirror_mode() == 0:
                    self._set_memory(d, a - 0x0400)
                    # Mirrors
                    if a < 0x2F00:
                        self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0C00)
                elif self._mapper.mirror_mode() == 1:
                    self._set_memory(d, a - 0x0800)
                    # Mirrors
                    if a < 0x2F00:
                        self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0800)
                elif self._mapper.mirror_mode() == 2:
                    self._set_memory(d, a - 0x0400)
                    self._set_memory(d, a - 0x0800)
                    # Mirrors
                    if a < 0x2F00:
                        self._set_memory(d, a + 0x1000)
                    self._set_memory(d, a + 0x0C00)
                    self._set_memory(d, a + 0x0800)

                # Escribimos en la posición indicada
                self._set_memory(d, a)
            # Mirrors Name Tables y Attr Tables
            elif 0x3000 <= a < 0x3F00:
                self.write_data(d, a - 0x1000)
            # Paletas
            elif 0x3F00 <= a < 0x3F20:
                # Si se escribe en el elemento de background o su mirror se escribe el valor de background
                # en todas las paletas mod 4 (pero no al contrario)
                if a == 0x3F00 or a == 0x3F10:
                    for x in range(0x3F00, 0x4000, 0x04):
                        self._set_memory(d, x)
                # Si no es un elemento de background escribimos normalmente la paleta
                elif a & 0x03 != 0:
                    # Escribe en mirrors
                    self._set_memory(d, a + 0x0020)
                    self._set_memory(d, a + 0x0040)
                    self._set_memory(d, a + 0x0060)
                    self._set_memory(d, a + 0x0080)
                    self._set_memory(d, a + 0x00A0)
                    self._set_memory(d, a + 0x00C0)
                    self._set_memory(d, a + 0x00E0)

                    # Escribimos en la posición indicada
                    self._set_memory(d, a)
            # Mirrors paletas
            elif 0x3F20 <= a < 0x4000:
                self.write_data(d, ((a - 0x3F20) % 0x0020) + 0x3F00)

        # Mirrors generales
        elif a >= 0x4000:
            self.write_data(d, a % 0x4000)


    # Funciones de ayuda

    # Establece el valor de una posición de memoria con los mirrors
    def _set_memory(self, d, addr):
        a = addr & 0x3FFF
        self._memory[a] = d
        self._memory[a + 0x4000] = d
        self._memory[a + 0x8000] = d
        self._memory[a + 0xC000] = d

