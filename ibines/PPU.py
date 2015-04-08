# -*- coding: utf-8 -*-

from PPUMemory import PPUMemory
from GFX import GFX

################################################################################
# Clase que implementa la PPU 2C02
################################################################################
class PPU(object):

    def __init__(self):
        #######################################################################
        # Variables de instancia
        #######################################################################
        # Memoria de la PPU
        self._memoria = PPUMemory(self)

        # Motor gráfico del emulador
        self._gfx = GFX()

        # Registros
        self._reg_control_1 = 0x00            # Dirección 0x2000 - write
        self._reg_control_2 = 0x00            # Dirección 0x2001 - write
        self._reg_status = 0x00               # Dirección 0x2002 - read
        self._reg_spr_addr = 0x00             # Dirección 0x2003 - write
        self._reg_spr_io = 0x00               # Dirección 0x2004 - write
        self._reg_vram_tmp = 0x00             # Dirección 0x2005 y 0x2006 - write (16-bit)
        self._reg_vram_addr = 0x00            # Dirección 0x2006 - write (16-bit)
        self._reg_vram_io = 0x00              # Dirección 0x2007 - read/write
        self._reg_sprite_dma = 0x00           # Dirección 0x4014 - write

        self._reg_x_offset = 0x0             # Scroll patrón (3-bit)

        self._reg_vram_switch = 0            # Indica si estamos en la 1ª(0) o 2ª(1) escritura de los registros vram
        #######################################################################
        #######################################################################

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
            self.write_reg_vram_tmp(data)
        elif addr == 0x2006:
            self.write_reg_vram_addr(data)
        elif addr == 0x2007:
            self.write_reg_vram_io(data)

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

    def write_reg_vram_tmp(self, data):
        self._reg_vram_tmp = data & 0xFF

    def write_reg_vram_addr(self, data):
        self._reg_vram_addr = data & 0xFF

    def write_reg_vram_io(self, data):
        d = data & 0xFF
        a = self._reg_vram_tmp
        self._reg_vram_io = d
        self._memoria.write_data(d, a)

    # Escribe el registro y hace una transferencia dma
    def write_sprite_dma(self, cpu_mem, src_addr):
        self._reg_sprite_dma = src_addr

        a = (src_addr & 0xFF) * 0x0100
        n = 0
        while n < 256:
            d = cpu_mem.read_data(a)
            self._memoria.write_sprite_data(d, n)
            a += 1
            n += 1


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


    # TODO: paracticamente todo
    # FUNCIONES DE DIBUJADO

    # Función que pinta la pantalla
    def draw_background(self):
        # Calcula el name table que se usará
        nt = self.control_1_name_table_bits_0_1()
        if nt == 0x0:
            nt_addr = 0x2000
        elif nt == 0x1:
            nt_addr = 0x2400
        if nt == 0x2:
            nt_addr = 0x2800
        if nt == 0x3:
            nt_addr = 0x2C00

        #Calcula el pattern table que se usará
        pt = self.control_1_background_pattern_bit_4()

        # Va pintando los patrones del fondo en la pantalla
        for x in range(32):
            for y in range(30):
                pattern_number = self._memoria.read_data(nt_addr)
                pattern = self._memoria.read_pattern(pt, pattern_number)
                self._draw_pattern(pattern, x, y)
                nt_addr += 1

    # TODO: MUCHO CURRO POR DELANTE
    # Dibuja el pattern almacenado en la lista en la posición
    # (x, y) de la pantalla
    def _draw_pattern(pattern, x, y):
        p1 = pattern[0:8]
        p2 = pattern[8:16]


    #######################################################################
    # Variables de clase
    #######################################################################
    # Paleta de colores:
    _COLOUR_PALETTE = [(0x75, 0x75, 0x75),    #0x00
                       (0x27, 0x1B, 0x8F),    #0x01
                       (0x00, 0x00, 0xAB),    #0x02
                       (0x47, 0x00, 0x9F),    #0x03
                       (0x8F, 0x00, 0x77),    #0x04
                       (0xAB, 0x00, 0x13),    #0x05
                       (0xA7, 0x00, 0x00),    #0x06
                       (0x7F, 0x0B, 0x00),    #0x07
                       (0x43, 0x2F, 0x00),    #0x08
                       (0x00, 0x47, 0x00),    #0x09
                       (0x00, 0x51, 0x00),    #0x0A
                       (0x00, 0x3F, 0x17),    #0x0B
                       (0x1B, 0x3F, 0x5F),    #0x0C
                       (0x00, 0x00, 0x00),    #0x0D
                       (0x00, 0x00, 0x00),    #0xOE
                       (0x00, 0x00, 0x00),    #0x0F
                       (0xBC, 0xBC, 0xBC),    #0x10
                       (0x00, 0x73, 0xEF),    #0x11
                       (0x23, 0x3B, 0xEF),    #0x12
                       (0x83, 0x00, 0xF3),    #0x13
                       (0xBF, 0x00, 0xBF),    #0x14
                       (0xE7, 0x00, 0x5B),    #0x15
                       (0xDB, 0x2B, 0x00),    #0x16
                       (0xCB, 0x4F, 0x0F),    #0x17
                       (0x8B, 0x73, 0x00),    #0x18
                       (0x00, 0x97, 0x00),    #0x19
                       (0x00, 0xAB, 0x00),    #0x1A
                       (0x00, 0x93, 0x3B),    #0x1B
                       (0x00, 0x83, 0x8B),    #0x1C
                       (0x00, 0x00, 0x00),    #0x1D
                       (0x00, 0x00, 0x00),    #0x1E
                       (0x00, 0x00, 0x00),    #0x1F
                       (0xFF, 0xFF, 0xFF),    #0x20
                       (0x3F, 0xBF, 0xFF),    #0x21
                       (0x5F, 0x97, 0xFF),    #0x22
                       (0xA7, 0x8B, 0xFD),    #0x23
                       (0xF7, 0x7B, 0xFF),    #0x24
                       (0xFF, 0x77, 0xB7),    #0x25
                       (0xFF, 0x77, 0x63),    #0x26
                       (0xFF, 0x9B, 0x3B),    #0x27
                       (0xF3, 0xBF, 0x3F),    #0x28
                       (0x83, 0xD3, 0x13),    #0x29
                       (0x4F, 0xDF, 0x4B),    #0x2A
                       (0x58, 0xF8, 0x98),    #0x2B
                       (0x00, 0xEB, 0xDB),    #0x2C
                       (0x00, 0x00, 0x00),    #0x2D
                       (0x00, 0x00, 0x00),    #0x2E
                       (0x00, 0x00, 0x00),    #0x2F
                       (0xFF, 0xFF, 0xFF),    #0x30
                       (0xAB, 0xE7, 0xFF),    #0x31
                       (0xC7, 0xD7, 0xFF),    #0x32
                       (0xD7, 0xCB, 0xFF),    #0x33
                       (0xFF, 0xC7, 0xFF),    #0x34
                       (0xFF, 0xC7, 0xDB),    #0x35
                       (0xFF, 0xBF, 0xB3),    #0x36
                       (0xFF, 0xDB, 0xAB),    #0x37
                       (0xFF, 0xE7, 0xA3),    #0x38
                       (0xE3, 0xFF, 0xA3),    #0x39
                       (0xAB, 0xF3, 0xBF),    #0x3A
                       (0xB3, 0xFF, 0xCF),    #0x3B
                       (0x9F, 0xFF, 0xF3),    #0x3C
                       (0x00, 0x00, 0x00),    #0x3D
                       (0x00, 0x00, 0x00),    #0x3E
                       (0x00, 0x00, 0x00)]    #0x3F
