# -*- coding: utf-8 -*-

import nesutils
import time
from PPUMemory import PPUMemory
from SpriteMemory import SpriteMemory
from GFX import *

"""
PPU

Descripción: Implementa el procesador gráfico de la NES
"""
class PPU(object):
    ###########################################################################
    # Constantes
    ###########################################################################
    FRAME_CYCLES = 33072
    SCANLINE_CYCLES = 106
    VBLANK_CYCLES = 7420
    FRAME_SCANLINES = 312
    VBLANK_SCANLINES = 70
    FRAME_PERIOD = 0.020        # Periodo de frame en segundos

    FRAME_WIDTH = 256
    FRAME_HEIGHT = 240

    def __init__(self, rom):
        #######################################################################
        # Variables de instancia
        #######################################################################
        # Memoria de la PPU
        self._memory = PPUMemory(self, rom)
        self._sprite_memory = SpriteMemory()

        # Motor gráfico del emulador
        self._gfx = GFX_Pygame()

        # Ciclos restantes hasta próximo evento
        self._cycles_frame = self.FRAME_CYCLES - 1
        self._cycles_scanline = self.SCANLINE_CYCLES - 1

        # Indica si hemos terminado con algo de lo indicado
        self._end_frame = False
        self._end_scanline = False

        # Scanline actual
        self._scanline_number = 0

        # Interrupciones
        self._int_vblank = 0

        # Registros

        # Registros I/O
        self._reg_control_1 = 0x00            # Dirección 0x2000 - write
        self._reg_control_2 = 0x00            # Dirección 0x2001 - write
        self._reg_status = 0x00               # Dirección 0x2002 - read
        self._reg_spr_addr = 0x00             # Dirección 0x2003 - write
        self._reg_spr_io = 0x00               # Dirección 0x2004 - write
        self._reg_vram_tmp = 0x00             # Dirección 0x2005 y 0x2006 - write (16-bit)
        self._reg_vram_addr = 0x00            # Dirección 0x2006 - write (16-bit)
        self._reg_vram_io = 0x00              # Dirección 0x2007 - read/write
        self._reg_sprite_dma = 0x00           # Dirección 0x4014 - write

        # Registros estado
        self._reg_x_offset = 0x0             # Scroll patrón (3-bit)
        self._reg_vram_switch = 0            # Indica si estamos en la 1ª(0) o 2ª(1) escritura de los registros vram
        self._reg_mirroring = 0x0            # 0x0: horizontal; 0x1: vertical: 0x2: single; 0x3: 4-screen

        #######################################################################
        #######################################################################


    # TODO: toda la chicha
    # Ejecuta un ciclo de reloj. Aquí va toda la chicha del dibujado y de
    # activación de cosas en función del ciclo del frame en el que nos
    # encontremos
    def exec_cycle(self, cycles):
        # Decrementamos el contador de ciclos
        if self._cycles_frame < cycles:
            self._cycles_frame = (self._cycles_frame - cycles) % PPU.FRAME_CYCLES
            self._end_frame = True
        else:
            self._cycles_frame -= cycles


        if self._cycles_scanline < cycles:
            self._cycles_scanline = (self._cycles_scanline - cycles) % PPU.SCANLINE_CYCLES
            self._end_scanline = True
        else:
            self._cycles_scanline -= cycles


        if not self._end_frame:     # En mitad del frame
            # Procesamos scanline en el ciclo de reloj adecuado
            if self._end_scanline:
                self.draw_scanline()
                self._gfx.update()
                self._scanline_number = (self._scanline_number + 1) % PPU.FRAME_SCANLINES
                self._end_scanline = False

            if self._cycles_frame < self.VBLANK_CYCLES and not self.is_vblank():     # Este es el ciclo en el que entramos en VBLANK
                self.start_vblank()    # Activamos el período VBLANK al inicio del período

        elif self._end_frame:     # Fin del Frame
            self.end_vblank() # Finalizamos el período VBLANK
            self._reg_vram_addr = self._reg_vram_tmp     # Esto es así al principio de cada frame
            self._end_frame = False


    # Lee el registro indicado por su dirección en memoria
    def read_reg(self, addr):
        d = 0x00

        if addr == 0x2002:
            d = self.read_reg_2002()
        elif addr == 0x2007:
            d = self.read_reg_2007()

        return d


    # Según el documento SKINNY.TXT
    def read_reg_2002(self):
        self._reg_vram_switch = 0
        return self._reg_status


    def read_reg_2007(self):
        data = self._memory.read_data(self._reg_vram_addr)
        self._reg_vram_io = data
        return data


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
        self._memory.write_sprite_data(d, self._reg_spr_addr)


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
        self._memory.write_data(d, a)


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

    def incr_xscroll(self):
        r = self._reg_vram_addr
        self._reg_x_offset = (self._reg_x_offset + 1) % 8
        bit_10 = (r & 0x0400) >> 10
        bits_0_4 = r & 0x001F

        if self._reg_x_offset == 0:
            bits_0_4 = (bits_0_4 + 1) % 32

            if bits_0_4 == 0x0:
                bit_10 = ~bit_10 & 0x1

        r = (r & 0xFBE0) | (bit_10 << 10) | bits_0_4

        self._reg_vram_addr = r


    def incr_yscroll(self):
        r = self._reg_vram_addr
        y_offset = (((r & 0x7000) >> 13) + 1) % 8
        bit_11 = (r & 0x0800) >> 11
        bits_5_9 = (r & 0x03E0) >> 5

        if y_offset == 0:
            bits_5_9 = (bits_5_9 + 1) % 30

            if bits_5_9 == 0x0:
                bit_11 = ~bit_11 & 0x1

        r = (r & 0x41F) | (y_offset << 12) | (bit_11 << 11) | (bits_5_9 << 5)

        self._reg_vram_addr = r


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


    # Inicia un período VBLANK
    def start_vblank(self):
        self._reg_status = nesutils.set_bit(self._reg_status, 7, 1)

        if self._reg_control_1 & 0x80:
            self._int_vblank = 1


    # Finaliza un período VBLANK
    def end_vblank(self):
        self._reg_status = self._reg_status & 0x7F


    # Devuelve si hay una solicitud de interrupción vblank
    def get_int_vblank(self):
        return self._int_vblank

    # Establece el valor de la solicitud de interrupción vblank
    def set_int_vblank(self, value):
        self._int_vblank = value


    # Indica si nos encontramos en un periodo VBLANK
    def is_vblank(self):
        return nesutils.get_bit(self._reg_status, 7)

    # FIXME: optimizar esta función que es la que se come toda la potencia (en draw_pixel())
    def draw_scanline(self):
        if 1 <= self._scanline_number <= 240:
            # Copia el desplazamiento X del registro tmp al addr al principio del scanline
            tmp = self._reg_vram_tmp

            self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 0, tmp & 0x0001)
            self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 1, tmp & 0x0002)
            self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 2, tmp & 0x0004)
            self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 3, tmp & 0x0008)
            self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 4, tmp & 0x0010)

            self._reg_vram_addr = nesutils.set_bit(self._reg_vram_addr, 10, tmp & 0x0400)

            for x in range(PPU.FRAME_WIDTH):
                self.draw_pixel(x, self._scanline_number - 1)
                self.incr_xscroll()

            self.incr_yscroll()

    # TODO: Función de prueba. Eliminar cuando funcione.
    def draw_scanline_test(self):
        for x in range(PPU.FRAME_WIDTH):
            if self._scanline_number > 0 and self._scanline_number < 241:
                self._gfx.draw_pixel(x, self._scanline_number - 1, (255,0,0))


    # Dibuja un pixel de la pantalla
    def draw_pixel(self, x, y):
        #sprites_pt = self.control_1_sprites_pattern_bit_3()
        #background_pt = self.control_1_background_pattern_bit_4()
        #sprite_size = self.control_1_sprites_size_bit_5()
        # Dibuja el fondo
        pattern_pixel_x = x % 8
        pattern_pixel_y = y % 8

        pattern_table = self.control_1_background_pattern_bit_4()
        pattern_index = self._memory.read_data(self._reg_vram_addr)

        # TODO: cambiar el color para los patrones calculando el color adecuado de la tabla de atributos
        pattern_rgb = self.get_pattern_rgb(pattern_table, pattern_index, 0, PPUMemory.ADDR_IMAGE_PALETTE)
        self._gfx.draw_pixel(x, y, pattern_rgb[pattern_pixel_x][pattern_pixel_y])

        # Dibuja los sprites
        sprites_list = self.get_sprites_list()
        for s in sprites_list:
            if y >= s.get_offset_y()  and y <=(s.get_offset_y() + 8):
                self.draw_sprite_pixel(s, x, y)


    def draw_sprite_pixel(self, sprite, x, y):
        off_x = sprite.get_offset_x()
        off_y = sprite.get_offset_y()

        if x >= off_x and x < off_x+8:
            if y >= off_y and y < off_y+8:
                pixel_x = x - off_x
                pixel_y = y - off_y

                pattern_table = self.control_1_sprites_pattern_bit_3()
                pattern_rgb = self.get_pattern_rgb(pattern_table, sprite.get_index(), sprite.get_attr_color(), PPUMemory.ADDR_SPRITE_PALETTE)

                self._gfx.draw_pixel(x, y, pattern_rgb[pixel_x][pixel_y])

    # Devuelve una lista de objetos de clase Sprite con los sprites de la memoria de sprites
    # FIX: Esto habría que reorganizarlo para que quede más claro
    def get_sprites_list(self):
        sprites_list = []
        for addr in range(0x00,0xFF,0x04):
            sprite = Sprite()
            sprite.load_by_addr(self._sprite_memory, addr)
            sprites_list.append(sprite)

        return sprites_list



    # Lee de la memoria de patrones un patrón especificado por su índice y lo
    # devuelve como una lista 8x8 en la que cada posición es una tupla
    # (R,G,B) con el color calculado de cada pixel
    # TODO: adaptar la paleta a si se está trabajando en fondo o sprites
    def get_pattern_rgb(self, pattern_table, pattern_index, attr_color, palette_addr):
        pattern = self.get_pattern_mem(pattern_table, pattern_index)

        pattern_rgb=[[(0, 0, 0)] * 8] * 8
        # Procesa los bytes del patrón para formatearlos en el valor de retorno
        for y in range(8):
            byte_1 = pattern[y]
            byte_2 = pattern[y + 8]

            for x in range(8):
                # Calcula la dirección del color en la paleta de memoria y lo extrae de la tabla de colores
                addr_color = palette_addr + (0x00 | ((byte_1 & (0x01 << x)) >> x) | (((byte_2 & (0x01 << x)) >> x) << 1) | ((attr_color & 0x03) << 2))
                color_index = self._memory.read_data(addr_color)
                rgb = self._COLOUR_PALETTE[color_index]

                # FIX: puede que esté al revés el patrón. Veremos como aparece Mario.
                # Asigna el valor RGB a la posición correspondiente:
                pattern_rgb[x][y] = rgb

        return pattern_rgb

    # Devuelve los 16 bytes del patrón indicado tal como se almacenan en la tabla de patrones especificada
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


    # Devuelve y establece el valor del mirroring
    def get_mirroring(self):
        return self._reg_mirroring

    def set_mirroring(self, m):
        self._reg_mirroring = m



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

