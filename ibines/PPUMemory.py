# -*- coding: utf-8 -*-

class PPUMemory(object):

    def __init__(self, ppu):
        self._ppu = ppu

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
                data = self._name_attr_1[a % 0x0040]
            elif self._mirror_mode == 1:
                data = self._name_attr_0[a % 0x0040]
        # Mirrors name/attr tables:
        elif a >= 0x3000 and a <= 0x3EFF:
            data = self.read_data(0x2000 + (a % 0x0F00))
        # Image Palette:
        elif a >= 0x3F00 and a <= 0x3F0F:
            data = self._image_palette[a % 0x0010]
        # Sprite Palette:
        elif a >= 0x3F10 and a <= 0x3F1F:
            data = self._sprite_palette[a % 0x0010]
        # Mirrors Palettes:
        elif a >= 0x3F20 and a <= 0x3FFF:
            data = self.read_data(0x3F00 + (a % 0x20))
        # Mirrors generales:
        elif a >= 0x4000 and a <= 0xFFFF:
            data = self.read_data(a % 0x4000)

        return data

    # Escribe un dato en la memoria de la PPU
    def write_data(data, addr):
        pass

    ############################################################################
    # Miembros privados
    ############################################################################
    _pattern_table_0 = []
    _pattern_table_1 = []

    _name_table_0 = []
    _attr_table_0 = []

    _name_table_1 = []
    _attr_table_1 = []

    _image_palette = []
    _sprite_palette = []

    # Referencia a la PPU
    _ppu = None

    # TODO: completar inicialización del modo mirror
    _mirror_mode = 0x0        # Modo de mirror de los "name tables" (sacado de la ROM). 0: horizontal, 1: vertical