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
        self._pattern_table = [0x00] * 0x2000

        self._name_table_0 = [0x00] * 0x03C0
        self._attr_table_0 = [0x00] * 0x0040

        self._name_table_1 = [0x00] * 0x03C0
        self._attr_table_1 = [0x00] * 0x0040

        self._image_palette = [0x00] * 0x0010
        self._sprite_palette = [0x00] * 0x0010

        # Referencia a la PPU
        self._ppu = ppu

        # Referencia a la ROM
        self._rom = rom
        if self._rom.get_chr_count() == 1:
            self._pattern_table = self._rom.get_chr()

        # TODO: completar inicialización del modo mirror
        self._mirror_mode = 0x0        # Modo de mirror de los "name tables" (sacado de la ROM). 0: horizontal, 1: vertical
        #######################################################################
        #######################################################################


    #Lee un dato de la memoria de la PPU:
    def read_data(self, addr):
        a = addr & 0xFFFF
        data = 0x00
        # Pattern tables:
        if a < 0x2000:
            data = self._pattern_table[a]
        # Name Tables y Attr Tables
        elif a < 0x23C0:
            data = self._name_table_0[a % 0x3C0]
        elif a < 0x2400:
            data = self._attr_table_0[a & 0x040]
        elif a < 0x27C0:
            if self._mirror_mode == 0:
                data = self._name_table_0[a % 0x3C0]
            elif self._mirror_mode == 1:
                data = self._name_table_1[a % 0x3C0]
        elif a < 0x2800:
            if self._mirror_mode == 0:
                data = self._attr_table_0[a % 0x3C0]
            elif self._mirror_mode == 1:
                data = self._attr_table_1[a & 0x040]
        elif a < 0x2BC0:
            if self._mirror_mode == 0:
                data = self._name_table_1[a % 0x3C0]
            elif self._mirror_mode == 1:
                data = self._name_table_0[a % 0x3C0]
        elif a < 0x2C00:
            if self._mirror_mode == 0:
                data = self._attr_table_1[a & 0x040]
            elif self._mirror_mode == 1:
                data = self._attr_table_0[a & 0x040]
        elif a < 0x2FC0:
            if self._mirror_mode == 0:
                data = self._name_table_1[a % 0x3C0]
            elif self._mirror_mode == 1:
                data = self._name_table_0[a % 0x3C0]
        elif a < 0x3000:
            if self._mirror_mode == 0:
                data = self._attr_table_1[a & 0x040]
            elif self._mirror_mode == 1:
                data = self._attr_table_0[a & 0x040]
        # Mirrors name/attr tables:
        elif a < 0x3F00:
            data = self.read_data(d, 0x2000 + (a % 0x0F00))
        # Image Palette:
        elif a < 0x3F10:
            if (a % 0x04) == 0:
                data = self._image_palette[0x00]
            else:
                data = self._image_palette[a % 0x0010]
        # Sprite Palette:
        elif a >= 0x3F10 and a <= 0x3F1F:
            if (a % 0x04) == 0:
                data = self._image_palette[0x00]
            else:
                data = self._sprite_palette[a % 0x0010]
        # Mirrors Palettes:
        elif a >= 0x3F20 and a <= 0x3FFF:
            data = self.read_data(d, 0x3F00 + (a % 0x20))
        # Mirrors generales:
        elif a >= 0x4000 and a <= 0xFFFF:
            data = self.read_data(d, a % 0x4000)

        return data

    # Escribe un dato en la memoria de la PPU
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF
        # Pattern tables:
        if a < 0x2000:
            if self._rom.get_chr_count() == 0:
                self._pattern_table_[a] = d
        # Name tables y attribute tables:
        elif a < 0x23C0:
            self._name_table_0[a % 0x03C0] = d
        elif a < 0x2400:
            self._attr_table_0[a % 0x0040] = d
        elif a < 0x27C0:
            if self._mirror_mode == 0:
                self._name_table_0[a % 0x03C0] = d
            elif self._mirror_mode == 1:
                self._name_table_1[a % 0x03C0] = d
        elif a < 0x2800:
            if self._mirror_mode == 0:
                self._attr_table_0[a % 0x0040] = d
            elif self._mirror_mode == 1:
                self._attr_table_1[a % 0x0040] = d
        elif a < 0x2BC0:
            if self._mirror_mode == 0:
                self._name_table_1[a % 0x03C0] = d
            elif self._mirror_mode == 1:
                self._name_table_0[a % 0x03C0] = d
        elif a < 0x2C00:
            if self._mirror_mode == 0:
                self._attr_table_1[a % 0x0040] = d
            elif self._mirror_mode == 1:
                self._attr_table_0[a % 0x0040] = d
        elif a < 0x2FC0:
            if self._mirror_mode == 0:
                self._name_table_1[a % 0x03C0] = d
            elif self._mirror_mode == 1:
                self._name_table_0[a % 0x03C0] = d
        elif a < 0x3000:
            if self._mirror_mode == 0:
                self._attr_table_1[a % 0x0040] = d
            elif self._mirror_mode == 1:
                self._attr_table_0[a % 0x0040] = d
        # Mirrors name/attr tables:
        elif a < 0x3F00:
            self.write_data(d, 0x2000 + (a % 0x0F00))
        # Image Palette:
        elif a < 0x3F10:
            print "Escribe en paleta"
            if (a % 0x04) == 0:
                self._image_palette[0x00] = d
            else:
                self._image_palette[a % 0x0010] = d
        # Sprite Palette:
        elif a < 0x3F20:
            if (a % 0x04) == 0:
                self._image_palette[0x00] = d
            else:
                self._sprite_palette[a % 0x0010] = d
        # Mirrors Palettes:
        elif a < 0x4000:
            self.write_data(d, 0x3F00 + (a % 0x20))
        # Mirrors generales:
        elif a < 0x10000:
            self.write_data(d, a % 0x4000)


    # Funciones de ayuda
    # Devuelve un patrón de la pattern table
    def read_pattern(self, table, pattern_number):
        addr = pattern_number * 0x0010
        pattern = []
        if table == 0:
            pattern = self.self._pattern_table[addr:addr + 16]
        elif table == 1:
            addr = addr + 0x1000
            pattern = self.self._pattern_table[addr:addr + 16]

        return pattern


