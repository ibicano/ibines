# -*- coding: utf-8 -*-

"""
PPUMemory

Descripción: Implementa la Memoria del procesador gráfico
"""
class PPUMemory(object):

    def __init__(self, ppu):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._pattern_table_0 = [None] * 0x1000
        self._pattern_table_1 = [None] * 0x1000

        self._name_table_0 = [None] * 0x03C0
        self._attr_table_0 = [None] * 0x0040

        self._name_table_1 = [None] * 0x03C0
        self._attr_table_1 = [None] * 0x0040

        self._image_palette = [None] * 0x0010
        self._sprite_palette = [None] * 0x0010

        # Referencia a la PPU
        self._ppu = ppu

        # TODO: completar inicialización del modo mirror
        self._mirror_mode = 0x0        # Modo de mirror de los "name tables" (sacado de la ROM). 0: horizontal, 1: vertical
        #######################################################################
        #######################################################################


    #Lee un dato de la memoria de la PPU:
    def read_data(self, addr):
        a = addr & 0xFFFF
        data = 0x00
        # Pattern tables:
        if a >= 0x0000 and a <= 0x0FFF:
             data = self._pattern_table_0[a % 0x1000]
        elif a >= 0x1000 and a <= 0x1FFF:
             data = self._pattern_table_1[a % 0x1000]
        # Name tables y attribute tables:
        elif a >= 0x2000 and a <= 0x23BF:
            data = self._name_table_0[a % 0x03C0]
        elif a >= 0x23C0 and a <= 0x23FF:
            data = self._attr_table_0[a % 0x0040]
        elif a >= 0x2400 and a <= 0x27BF:
            if self._mirror_mode == 0:
                data = self._name_table_0[a % 0x03C0]
            elif self._mirror_mode == 1:
                data = self._name_table_1[a % 0x03C0]
        elif a >= 0x27C0 and a <= 0x27FF:
            if self._mirror_mode == 0:
                data = self._attr_table_0[a % 0x0040]
            elif self._mirror_mode == 1:
                data = self._attr_table_1[a % 0x0040]
        elif a >= 0x2800 and a <= 0x2BBF:
            if self._mirror_mode == 0:
                data = self._name_table_1[a % 0x03C0]
            elif self._mirror_mode == 1:
                data = self._name_table_0[a % 0x03C0]
        elif a >= 0x2BC0 and a <= 0x2BFF:
            if self._mirror_mode == 0:
                data = self._attr_table_1[a % 0x0040]
            elif self._mirror_mode == 1:
                data = self._attr_table_0[a % 0x0040]
        elif a >= 0x2C00 and a <= 0x2FBF:
            if self._mirror_mode == 0:
                data = self._name_table_1[a % 0x03C0]
            elif self._mirror_mode == 1:
                data = self._name_table_0[a % 0x03C0]
        elif a >= 0x2FC0 and a <= 0x2FFF:
            if self._mirror_mode == 0:
                data = self._attr_table_1[a % 0x0040]
            elif self._mirror_mode == 1:
                data = self._attr_table_0[a % 0x0040]
        # Mirrors name/attr tables:
        elif a >= 0x3000 and a <= 0x3EFF:
            data = self.read_data(0x2000 + (a % 0x0F00))
        # Image Palette:
        elif a >= 0x3F00 and a <= 0x3F0F:
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
            data = self.read_data(0x3F00 + (a % 0x20))
        # Mirrors generales:
        elif a >= 0x4000 and a <= 0xFFFF:
            data = self.read_data(a % 0x4000)

        return data

    # Escribe un dato en la memoria de la PPU
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF
        # Pattern tables:
        if a >= 0x0000 and a <= 0x0FFF:
             self._pattern_table_0[a % 0x1000] = d
        elif a >= 0x1000 and a <= 0x1FFF:
             self._pattern_table_1[a % 0x1000] = d
        # Name tables y attribute tables:
        elif a >= 0x2000 and a <= 0x23BF:
            self._name_table_0[a % 0x03C0] = d
        elif a >= 0x23C0 and a <= 0x23FF:
            self._attr_table_0[a % 0x0040] = d
        elif a >= 0x2400 and a <= 0x27BF:
            if self._mirror_mode == 0:
                self._name_table_0[a % 0x03C0] = d
            elif self._mirror_mode == 1:
                self._name_table_1[a % 0x03C0] = d
        elif a >= 0x27C0 and a <= 0x27FF:
            if self._mirror_mode == 0:
                self._attr_table_0[a % 0x0040] = d
            elif self._mirror_mode == 1:
                self._attr_table_1[a % 0x0040] = d
        elif a >= 0x2800 and a <= 0x2BBF:
            if self._mirror_mode == 0:
                self._name_table_1[a % 0x03C0] = d
            elif self._mirror_mode == 1:
                self._name_table_0[a % 0x03C0] = d
        elif a >= 0x2BC0 and a <= 0x2BFF:
            if self._mirror_mode == 0:
                self._attr_table_1[a % 0x0040] = d
            elif self._mirror_mode == 1:
                self._attr_table_0[a % 0x0040] = d
        elif a >= 0x2C00 and a <= 0x2FBF:
            if self._mirror_mode == 0:
                self._name_table_1[a % 0x03C0] = d
            elif self._mirror_mode == 1:
                self._name_table_0[a % 0x03C0] = d
        elif a >= 0x2FC0 and a <= 0x2FFF:
            if self._mirror_mode == 0:
                self._attr_table_1[a % 0x0040] = d
            elif self._mirror_mode == 1:
                self._attr_table_0[a % 0x0040] = d
        # Mirrors name/attr tables:
        elif a >= 0x3000 and a <= 0x3EFF:
            self.write_data(d, 0x2000 + (a % 0x0F00))
        # Image Palette:
        elif a >= 0x3F00 and a <= 0x3F0F:
            if (a % 0x04) == 0:
                self._image_palette[0x00] = d
            self._image_palette[a % 0x0010] = d
        # Sprite Palette:
        elif a >= 0x3F10 and a <= 0x3F1F:
            if (a % 0x04) == 0:
                self._image_palette[0x00] = d
            self._sprite_palette[a % 0x0010] = d
        # Mirrors Palettes:
        elif a >= 0x3F20 and a <= 0x3FFF:
            self.write_data(d, 0x3F00 + (a % 0x20))
        # Mirrors generales:
        elif a >= 0x4000 and a <= 0xFFFF:
            self.write_data(d, a % 0x4000)


    # Funciones de ayuda
    # Devuelve un patrón de la pattern table
    def read_pattern(self, table, pattern_number):
        addr = pattern_number * 0x0010
        pattern = []
        if table == 0:
            for i in range(16):
                pattern[i] = self._pattern_table_0[addr]
                addr += 1
        elif table == 1:
            for i in range(16):
                pattern[i] = self._pattern_table_1[addr]
                addr += 1

        return pattern


