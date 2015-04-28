# -*- coding: utf-8 -*-

import nesutils
import time
from PPUMemory import PPUMemory
from SpriteMemory import SpriteMemory
from GFX import *
from PPU import PPU

"""
PPU

Descripción: Implementa el procesador gráfico de la NES
"""
class FastPPU(PPU):
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
        self._gfx = GFX_PySdl2()

        # Ciclos restantes hasta próximo evento
        self._cycles_frame = self.FRAME_CYCLES - 1
        self._cycles_scanline = self.SCANLINE_CYCLES - 1

        # Indica si hemos terminado con algo de lo indicado
        self._end_frame = False
        self._end_scanline = False

        # Indica si tenemos que ller otro "pattern" de memoria o usamos el actual
        self._fetch_pattern = True

        # Scanline actual
        self._scanline_number = 0

        # Interrupciones
        self._int_vblank = 0

        # Variables que almacenan el patrón que se está procesando
        self._pattern_palette = [None] * 8
        for x in range(8):
            self._pattern_palette[x] = [0] * 8

        self._pattern_rgb = [None] * 8
        for x in range(8):
            self._pattern_rgb[x] = [(0, 0, 0)] * 8

        # Matriz de tiles:
        self._tiles_array = [None] * 960
        for x in range(960):
            self._tiles_array[x] = (0, 0, 0)

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
            self._cycles_frame = (self._cycles_frame - cycles) % FastPPU.FRAME_CYCLES
            self._end_frame = True
        else:
            self._cycles_frame -= cycles


        if self._cycles_scanline < cycles:
            self._cycles_scanline = (self._cycles_scanline - cycles) % FastPPU.SCANLINE_CYCLES
            self._end_scanline = True
        else:
            self._cycles_scanline -= cycles


        if not self._end_frame:     # En mitad del frame
            # Procesamos scanline en el ciclo de reloj adecuado
            if self._end_scanline:
                #self.draw_scanline()
                #self._gfx.update()
                self._scanline_number = (self._scanline_number + 1) % FastPPU.FRAME_SCANLINES
                self._end_scanline = False

            if self._cycles_frame < self.VBLANK_CYCLES and not self.is_vblank():     # Este es el ciclo en el que entramos en VBLANK
                self.draw_frame()
                self.start_vblank()    # Activamos el período VBLANK al inicio del período

        elif self._end_frame:     # Fin del Frame
            self.end_vblank() # Finalizamos el período VBLANK
            self._reg_vram_addr = self._reg_vram_tmp     # Esto es así al principio de cada frame
            self._end_frame = False



    # Dibuja el frame
    def draw_frame(self):

        self.read_name_table()

        for y in range(30):
            for x in range(32):
                n = 32 * y + x
                pattern = self._tiles_array[n]
                self.draw_pattern(pattern, x, y)

        self._gfx.update()


    # Dibuja un patrón en la posición 32x30 indicada
    def draw_pattern(self, pattern, x, y):

        for j in range(8):
            for i in range(8):
                pixel_x = 8*x + i
                pixel_y = 8*y + j
                self._gfx.draw_pixel(pixel_x, pixel_y, pattern[i][j])


    def read_name_table(self):

        for i in range(0x3C0):
            p_addr = self._memory.read_data(0x2000 + i)
            p_pal = self.fetch_pattern_palette(1, p_addr, 0)
            p_rgb = self.fetch_pattern_rgb(p_pal, 0x3F00)
            self._tiles_array[i] = p_rgb






    # Lee de la memoria de patrones un patrón especificado por su índice y lo
    # devuelve como una lista 8x8 en la que cada posición es una tupla
    # (R,G,B) con el color calculado de cada pixel
    # TODO: adaptar la paleta a si se está trabajando en fondo o sprites
    def fetch_pattern_palette(self, pattern_table, pattern_index, attr_color):
        pattern_palette = [None] * 8
        for x in range(8):
            pattern_palette[x] = [0] * 8

        pattern = self.fetch_pattern_mem(pattern_table, pattern_index)

        # Procesa los bytes del patrón para formatearlos en el valor de retorno
        for y in range(8):
            byte_1 = pattern[y]
            byte_2 = pattern[y + 8]

            for x in range(8):
                # Calcula la dirección del color en la paleta de memoria y lo extrae de la tabla de colores
                palette_index = (0x00 | ((byte_1 & (0x01 << x)) >> x) | (((byte_2 & (0x01 << x)) >> x) << 1) | ((attr_color & 0x03) << 2))

                # Asigna el índice de la paleta a la posición correspondiente:
                pattern_palette[7 - x][7 - y] = palette_index

        return pattern_palette


    def fetch_pattern_rgb(self, pattern_palette, palette_addr):

        pattern_rgb = [None] * 8
        for x in range(8):
            pattern_rgb[x] = [(0, 0, 0)] * 8

        for x in range(8):
            for y in range(8):
                #color_index = self._memory.read_data(palette_addr + self._pattern_palette[x][y])
                #rgb = self._COLOUR_PALETTE[color_index]
                #self._pattern_rgb[x][y] = rgb

                # Esto es para pruebas
                if pattern_palette[x][y]:
                    pattern_rgb[x][y] = (255, 255, 255)

        return pattern_rgb



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

