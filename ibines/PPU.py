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


    # Métodos para obtener información de los registros de control

    # Devuelve la "name table" activa
    def control_1_name_table_bits_0_1(self):
        r = self._reg_control_1 & 0x03
        return r

    # Devuelve el valor del bit que indica el incrmento de dirección
    # 1, si es 0 o 32 si es 1
    def control_1_increment_bit_2(self):
        r = (self._reg_control_1 & 0x04) >> 2
        return r

    def control_1_sprites_pattern_bit_3(self):
        r = (self._reg_control_1 & 0x08) >> 3
        return r

    def control_1_background_pattern_bit_4(self):
        r = (self._reg_control_1 & 0x10) >> 4
        return r

    def control_1_sprites_size_bit_5(self):
        r = (self._reg_control_1 & 0x20) >> 5
        return r

    def control_1_master_mode_bit_6(self):
        r = (self._reg_control_1 & 0x40) >> 6
        return r

    def control_1_NMI_bit_7(self):
        r = (self._reg_control_1 & 0x80) >> 7
        return r

    def control_2_monochrome_bit_0(self):
        r = (self._reg_control_2 & 0x01)
        return r

    def control_2_clip_background_bit_1(self):
        r = (self._reg_control_2 & 0x02) >> 1
        return r

    def control_2_clip_sprites_bit_2(self):
        r = (self._reg_control_2 & 0x04) >> 2
        return r

    def control_2_background_bit_3(self):
        r = (self._reg_control_2 & 0x08) >> 3
        return r

    def control_2_sprites_bit_4(self):
        r = (self._reg_control_2 & 0x10) >> 4
        return r

    def control_2_colour_config_bits_5_7(self):
        r = (self._reg_control_2 & 0xE0) >> 5
        return r

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