# -*- coding: utf-8 -*-

################################################################################
# Clase que implementa la PPU 2C02
################################################################################
class PPU(object):

    def __init__(self):
        pass

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

    def write_reg_control_1(self, data):
        self._reg_control_1 = data & 0xFF

    def write_reg_control_2(self, data):
        self._reg_control_2 = data & 0xFF

    def write_reg_spr_addr(self, data):
        self._reg_spr_addr = data & 0xFF

    def write_reg_spr_io(self, data):
        self._reg_spr_io = data & 0xFF

    def write_reg_vram_addr_1(self, data):
        self._reg_vram_addr_1 = data & 0xFF

    def write_reg_vram_addr_2(self, data):
        self._reg_vram_addr_2 = data & 0xFF

    def write_reg_vram_io(self, data):
        self._reg_vram_io = data & 0xFF

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