# -*- coding: utf-8 -*-

class PPUMemory(object):

    def __init__(self, ppu):
        self._ppu = ppu

    #Lee un dato de la memoria de la PPU:
    # TODO: completar la parte del mirror de las name tables
    def read_data(self, addr):
        a = addr & 0xFFFF
        data = 0x00
        # Pattern tables:
        if a >= 0x0000 and a <= 0x0FFF:
             data = self._pattern_table_0[a % 0x1000]
        elif a >= 0x1000 and a <= 0x1FFF:
             data = self._pattern_table_1[a % 0x1000]
        # Name tables:
        elif a >= 0x2000 and a <= 0x23BF:
            data = self._name_table_0[a % 0x03C0]
        elif a >= 0x2400 and a <= 0x27BF:
            if self._mirror_mode == 0:
                data = self._name_table_0[a % 0x03C0]
            elif self._mirror_mode == 1:
                data = self._name_table_1[a % 0x03C0]
        elif a >= 0x2800 and a <= 0x2BBF:
            if self._mirror_mode == 0:
                data = self._name_table_1[a % 0x03C0]
            elif self._mirror_mode == 1:
                data = self._name_table_0[a % 0x03C0]
        elif a >= 0x2C00 and a <= 0x2FBF:
            if self._mirror_mode == 0:
                data = self._name_table_1[a % 0x03C0]
            elif self._mirror_mode == 1:
                data = self._name_table_0[a % 0x03C0]

        # TODO: implementar Attribute table
        # TODO: implementar Mirrors
        # TODO: implementar resto de memoria

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

    _ppu = None

    # TODO: completar inicialización del modo mirror
    _mirror_mode = 0x0        # Modo de mirror de los "name tables" (sacado de la ROM). 0: horizontal, 1: vertical