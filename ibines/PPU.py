# -*- coding: utf-8 -*-

import nesutils
from PPUMemory import PPUMemory
from SpriteMemory import SpriteMemory
from GFX import GFX

"""
PPU

Descripción: Implementa el procesador gráfico de la NES
"""
class PPU(object):
    ###########################################################################
    # Constantes
    ###########################################################################
    FRAME_CYCLES = 33246
    SCANLINE_CYCLES = 106
    VBLANK_CYCLES = 7459
    FRAME_SCANLINES = 312
    VBLANK_SCANLINES = 70
    FRAME_PERIOD = 0.020        # Periodo de frame en milisegundos

    def __init__(self):
        #######################################################################
        # Variables de instancia
        #######################################################################
        # Memoria de la PPU
        self._memoria = PPUMemory(self)
        self._sprite_memory = SpriteMemory()

        # Motor gráfico del emulador
        self._gfx = GFX()

        # Ciclos de CPU ejecutados (para sincronización)
        self._cpu_cycles = 0

        # Ciclo en el que se entró en la última vblank
        self._vblank_cycle = self.VBLANK_CYCLES         # Retrasamos la VBLANK en el primer ciclo


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

    # TODO: terminar esto y la activación del bit VBLANK
    def set_cpu_cycles(self, cpu_cycles):
        self._cpu_cycles = cpu_cycles
        if (self._cpu_cycles - self._vblank_cycle) > self.FRAME_CYCLES:
            self.set_status_bit_7_vblank(1)
            self._vblank_cycle = cpu_cycles

    # Lee el registro indicado por su dirección en memoria
    def read_reg(self, data, addr):
        d = 0x00

        if addr == 0x2002:
            d = self.read_reg_2002()
        elif addr == 0x2007:
            d = self.get_vram_io()

        return d

    # Según el documento SKINNY.TXT
    def read_reg_2002(self):
        self._reg_vram_switch = 0
        return self.get_reg_status()

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


    # Según el documento SKINNY.TXT
    def write_reg_2000(self, data):
        d = data & 0xFF
        self._reg_control_1 = d

        # Transfiere el valor de los bits 0-1 a los bits 10-11 del registro vram_tmp
        self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 10, d & 0x01)
        self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 11, d & 0x02)

    def write_reg_control_2(self, data):
        self._reg_control_2 = data & 0xFF

    def write_reg_spr_addr(self, data):
        self._reg_spr_addr = data & 0xFF

    def write_reg_spr_io(self, data):
        d = data & 0xFF
        self._reg_spr_io = d
        self._memoria.write_sprite_data(d, self._reg_spr_addr)


    # Según el documento SKINNY.TXT
    def write_reg_2005(self, data):
        d = data & 0xFF

        # Primera escritura en $2005
        if self.reg_vram_switch == 0:
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 0, d & 0x08)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 1, d & 0x10)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 2, d & 0x20)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 3, d & 0x40)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 4, d & 0x80)

            self._reg_x_offset = d & 0x07
            self._reg_vram_switch = 1
        # Segunda escritura en $2005
        else:
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 5, d & 0x08)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 6, d & 0x10)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 7, d & 0x20)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 8, d & 0x40)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 9, d & 0x80)

            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 12, d & 0x01)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 13, d & 0x02)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 14, d & 0x04)

            self._reg_vram_switch = 0


    # Según el documento SKINNY.TXT
    def write_reg_2006(self, data):
        d = data & 0xFF

        # Primera escritura en $2006
        if self.reg_vram_switch == 0:
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 8, d & 0x01)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 9, d & 0x02)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 10, d & 0x04)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 11, d & 0x08)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 12, d & 0x10)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 13, d & 0x20)

            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 14, 0)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 15, 0)

            self._reg_vram_switch = 1
        # Segunda escritura en $2006
        else:
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 0, d & 0x01)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 1, d & 0x02)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 2, d & 0x04)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 3, d & 0x08)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 4, d & 0x10)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 5, d & 0x20)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 6, d & 0x40)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 7, d & 0x80)

            self._reg_vram_addr = self.reg_vram_tmp

            self._reg_vram_switch = 0


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
            self._sprite_memory.write_data(d, n)
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

    # Devuelve la dirección de la Name Table activa en los bits 0-1 del registro de control 1
    def active_name_table_addr(self):
        nt = self.control_1_name_table_bits_0_1()

        addr = None

        if nt == 0x0:
            addr = 0x2000
        elif nt == 0x1:
            addr = 0x2400
        elif nt == 0x2:
            addr = 0x2800
        elif nt == 0x3:
            addr = 0x2C00

        return addr



    # Lanza una interrupción VBLANK
    # TODO: completar función
    def set_vblank(self):
        pass


    # TODO: paracticamente todo
    # FUNCIONES DE DIBUJADO
    def draw_frame(self):
        for y in range(240):
            self._reg_vram_addr = self._reg_vram_tmp
            self.draw_scanline(y)
            self._gfx.update()
            self.set_vblank()


    def draw_scanline(self, y):
        # Copia el desplazamiento X del registro tmp al addr al principio del scanline
        tmp = self._reg_vram_tmp

        self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 0, tmp & 0x0001)
        self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 1, tmp & 0x0002)
        self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 2, tmp & 0x0004)
        self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 3, tmp & 0x0008)
        self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 4, tmp & 0x0010)

        self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 10, tmp & 0x0400)

        for x in range(256):
            self.draw_pixel(x, y)


    # TODO: implementar la función "get_pattern_rgb()" al que se le proporciona el
    # número de patrón y devuelve un matrix 8x8 con los colores de cada pixel
    # ya calculados como una tupla (R,G,B)
    def draw_pixel(self, x, y):
        #sprites_pt = self.control_1_sprites_pattern_bit_3()
        #background_pt = self.control_1_background_pattern_bit_4()
        #sprite_size = self.control_1_sprites_size_bit_5()

        # Dibuja el fondo
        pattern_pixel_x = x % 8
        pattern_pixel_y = y % 8

        pattern_index = self._memory.read_data(self._reg_vram_addr)
        pattern_rgb = self.get_pattern_rgb(pattern_index)
        self.gfx.draw_pixel(x, y, pattern_rgb[pattern_pixel_x][pattern_pixel_y])

        # Dibuja los sprites
        sprites_list = self.get_sprites_list()
        for s in sprites_list:
            if y >= s.get_offset_y()  and y <=(s.get_offset_y() + 8):
                self.draw_sprite_pixel(s, x, y)


    def draw_sprite_pixel(self, sprite, x, y):
        off_x = sprite.get_offset_x()
        off_y = sprite.get_offset_y()

        if x >= off_x and x > off_x+8:
            if y >= off_y and y < off_y+8:
                sprite_x = x - off_x
                sprite_y = y - off_y

                pt = self.control_1_sprites_pattern_bit_3()
                pattern_rgb = self.get_pattern_rgb(pt, sprite.get_index(), sprite.get_attr_color(), 0x3F10)

                self._gfx.draw_pixel(x, y, pattern_rgb[sprite_x][sprite_y])

    # Devuelve una lista de objetos de clase Sprite con los sprites de la memoria de sprites
    # FIX: Esto habría que reorganizarlo para que quede más claro
    def get_sprites_list(self):
        sprites_list = []
        for addr in range(0x00,0xFF,0x04):
            sprite = Sprite()
            sprite.load_by_addr(self.sprite_memory, addr)
            sprites_list.appen(sprite)

        return sprites_list



    # Lee de la memoria de patrones un patrón especificado por su índice y lo
    # devuelve como una lista 8x8 en la que cada posición es una tupla
    # (R,G,B) con el color calculado de cada pixel
    # TODO: adaptar la paleta a si se está trabajando en fondo o sprites
    def get_pattern_rgb(self, pattern_table, pattern_index, attr_color, palette_addr):
        pattern = self._get_pattern_mem(pattern_table, pattern_index)

        pattern_rgb=[]
        # Procesa los bytes del patrón para formatearlos en el valor de retorno
        for y in range(8):
            byte_1 = pattern[y]
            byte_2 = pattern[y+8]

            for x in range(8):
                # Calcula la dirección del color en la paleta de memoria y lo extrae de la tabla de colores
                addr_color = palette_addr + (0x00 | ((byte_1 & (0x01 << x)) >> x) | (((byte_2 & (0x01 << x)) >> x) << 1) | ((attr_color & 0x03) << 2))
                color_index = self._memory.read_data(addr_color)
                rgb = self._COLOUR_PALETTE(color_index)

                # FIX: puede que esté al revés el patrón. Veremos como aparece Mario.
                # Asigna el valor RGB a la posición correspondiente:
                pattern_rgb[x][y] = rgb

        return pattern_rgb


    def get_pattern_mem(self, pattern_table, pattern_index):
        if pattern_table == 0:
            addr = 0x0000
        else:
            addr = 0x1000

        addr = addr + pattern_index * 16

        # Lee los bytes del patrón de memoria y lo guarda en una lista
        pattern = []
        for a in range(addr, addr+16):
            pattern.append(self._memory.read_data(a))

        return pattern


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



# Clase que implmenta la info de un sprite de la ram de sprites
class Sprite(object):

    def __init__(self):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._offset_y = 0x00
        self._index = 0x00
        self._attributes = 0x00
        self._offset_x = 0x00
        #######################################################################


    def load_by_addr(self, sprite_memory, sprite_addr):
        self._offset_y = sprite_memory.read_data(sprite_addr)
        self._index = sprite_memory.read_data(sprite_addr)
        self._attributes = sprite_memory.read_data(sprite_addr)
        self._offset_x = sprite_memory.read_data(sprite_addr)


    def load_by_number(self, sprite_memory, sprite_number):
        sprite_addr = sprite_number * 4
        self.load_by_addr(sprite_memory, sprite_addr)


    def get_offset_x(self):
        return self._offset_x


    def get_offset_y(self):
        return self._offset_x


    def get_index(self):
        return self._index


    # Devuelve atributos:
    def get_attr_color(self):
        return self._attributes & 0x03

    def get_priority(self):
        return (self._attributes & 0x20) >> 5

    def get_horizontal_flip(self):
        return (self._attributes & 0x40) >> 6

    def get_vertical_flip(self):
        return (self._attributes & 0x40) >> 7

