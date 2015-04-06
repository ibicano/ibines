# -*- coding: utf-8 -*-

from PPUMemory import PPUMemory

################################################################################
# Clase que implementa la PPU 2C02
################################################################################
class PPU(object):

    def __init__(self):
        self._memoria = PPUMemory(self)

    # Lee el registro indicado por su dirección en memoria
    def read_reg(self, data, addr):
        d = 0x00

        if addr == 0x2002:
            d = self.get_reg_status()
        elif addr == 0x2007:
            d = self.get_vram_io()

        return d

    # Escribe el registro indicado por su dirección en memoria
    def write_reg(self, data, addr):
        if addr == 0x2000:
            self.write_reg_control_1(data)
        elif addr == 0x2001:
            self.write_reg_control_2(data)
        elif addr == 0x2003:
            self.write_reg_spr_addr(data)
        elif addr == 0x2004:
            self.write_reg_spr_io(data)
        elif addr == 0x2005:
            self.write_reg_vram_addr_1(data)
        elif addr == 0x2006:
            self.write_reg_vram_addr_2(data)
        elif addr == 0x2007:
            self.write_reg_vram_io(data)
        elif addr == 0x4014:
            self.write_reg_sprite_dma(data)

    def write_reg_control_1(self, data):
        self._reg_control_1 = data & 0xFF

    def write_reg_control_2(self, data):
        self._reg_control_2 = data & 0xFF

    def write_reg_spr_addr(self, data):
        self._reg_spr_addr = data & 0xFF

    def write_reg_spr_io(self, data):
        d = data & 0xFF
        self._reg_spr_io = d
        self._memoria.write_sprite_data(d, self._reg_spr_addr)

    def write_reg_vram_addr_1(self, data):
        self._reg_vram_addr_1 = data & 0xFF

    def write_reg_vram_addr_2(self, data):
        self._reg_vram_addr_2 = data & 0xFF

    def write_reg_vram_io(self, data):
        d = data & 0xFF
        a = (self._reg_vram_addr_2 << 8) | self._reg_vram_addr_1
        self._reg_vram_io = d
        self._memoria.write_data(d, a)


    def write_sprite_dma(self, data):
        self._sprite_dma = data & 0xFF

    ############################################################################
    # Miembros privados
    ############################################################################
    # Registros
    _reg_control_1 = 0x00            # Dirección 0x2000 - write
    _reg_control_2 = 0x00            # Dirección 0x2001 - write
    _reg_status = 0x00               # Dirección 0x2002 - read
    _reg_spr_addr = 0x00             # Dirección 0x2003 - write
    _reg_spr_io = 0x00               # Dirección 0x2004 - write
    _reg_vram_addr_1 = 0x00          # Dirección 0x2005 - write
    _reg_vram_addr_2 = 0x00          # Dirección 0x2006 - write
    _reg_vram_io = 0x00              # Dirección 0x2007 - read/write
    _reg_sprite_dma = 0x00           # Dirección 0x4014 - write

    # Memoria
    _memoria = None