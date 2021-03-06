# -*- coding: utf-8 -*-

import nesutils
import copy
from PPUMemory import PPUMemory
from SpriteMemory import SpriteMemory
from GFX import *
from Sprite import *

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

    def __init__(self, mapper):
        #######################################################################
        # Variables de instancia
        #######################################################################
        # Memoria de la PPU
        self._memory = PPUMemory(self, mapper)
        self._sprite_memory = SpriteMemory()

        # Mapper
        self._mapper = mapper

        # Motor gráfico del emulador
        self._gfx = GFX_PySdl2()

        # Ciclos restantes hasta próximo frame
        self._cycles_frame = self.FRAME_CYCLES - 1

        # Indica si hemos terminado con algo de lo indicado
        self._end_frame = False
        self._end_scanline = False

        # Indica si tenemos que leer otro "pattern" de memoria o usamos el actual
        self._fetch_pattern = True

        # Scanline actual
        self._scanline_number = 0

        # Número de scanlines pendientes
        self._scanlines_pending = 0

        # Lista de sprites a dibujar en el scanline actual
        self._sprites_scanline_number = 0
        self._sprites_scanline = []
        for s in range(9):
            self._sprites_scanline.append(Sprite(self))

        self._sprites_list = []
        for s in range(64):
            self._sprites_list.append(Sprite(self))

        self._sprite_zero = self._sprites_list[0]

        # Variables que almacenan el tile del sprite que se está procesando
        self._tile_sprite_zero_index_palette_0 = [None] * 8
        for x in range(8):
            self._tile_sprite_zero_index_palette_0[x] = [0] * 8

        self._tile_sprite_zero_rgb_0 = [None] * 8
        for x in range(8):
            self._tile_sprite_zero_rgb_0[x] = [(0, 0, 0)] * 8

        self._tile_sprite_zero_index_palette_1 = [None] * 8
        for x in range(8):
            self._tile_sprite_zero_index_palette_1[x] = [0] * 8

        self._tile_sprite_zero_rgb_1 = [None] * 8
        for x in range(8):
            self._tile_sprite_zero_rgb_1[x] = [(0, 0, 0)] * 8


        # Indica si ha avido ya un sprite hit en el frame
        self._sprite_hit = 0

        # Indica si los píxeles son de background transparentes (0), de background sólidos (1) o de sprite (2)
        self.pixel_background = [None] * 256
        for x in range(256):
            self.pixel_background[x] = [0] * 240

        # Interrupciones
        self._int_vblank = 0

        # Indica si ya se ha inicializado la vblank en este frame. Se resetea al finalizar el frame.
        # Sirve para controlar si ya se ha procesado o no el período VBLANK cuando estamos dentro de
        # él, ya que sólo debe procesarse una vez.
        self._started_vblank = 0

        # Buffer de lectura de la VRAM (la lectura del registro $2007 se entrega retrasada)
        self._vram_buffer = 0x00

        # Variables que almacenan el tile del fondo que se está procesando
        self._tile_bg_index_palette = [None] * 8
        for x in range(8):
            self._tile_bg_index_palette[x] = [0] * 8

        self._tile_bg_rgb = [None] * 8
        for x in range(8):
            self._tile_bg_rgb[x] = [(0, 0, 0)] * 8


        # Variables que almacenan el tile del sprite que se está procesando
        self._tile_sprite_index_palette = [None] * 8
        for x in range(8):
            self._tile_sprite_index_palette[x] = [0] * 8

        self._tile_sprite_rgb = [None] * 8
        for x in range(8):
            self._tile_sprite_rgb[x] = [(0, 0, 0)] * 8

        # Cache de Tiles:
        self._tiles_cache = {}

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
        self._tmp_y_offset = 0x0             # Alamcena el offset y de forma temporal para leerlo más rápido
        self._reg_vram_switch = 0            # Indica si estamos en la 1ª(0) o 2ª(1) escritura de los registros vram

        #######################################################################
        #######################################################################


    # Ejecuta un ciclo de reloj. Aquí va toda la chicha del dibujado y de
    # activación de cosas en función del ciclo del frame en el que nos
    # encontremos
    def exec_cycle(self, cycles):

        if self._cycles_frame < cycles:
            self._end_frame = True
            self._cycles_frame = (self._cycles_frame  - cycles) % PPU.FRAME_CYCLES
        else:
            self._cycles_frame = self._cycles_frame  - cycles


        scanlines_cycles = self._scanline_number * PPU.SCANLINE_CYCLES

        pending_scanlines = (((PPU.FRAME_CYCLES - scanlines_cycles) - self._cycles_frame) % PPU.FRAME_CYCLES) / PPU.SCANLINE_CYCLES

        while pending_scanlines > 0:
            # Dibujamos el scanline
            if 1 <= self._scanline_number <= 240:
                self.draw_scanline()
                self._mapper.scanline_tick()

            self._scanline_number = (self._scanline_number + 1) % PPU.FRAME_SCANLINES
            pending_scanlines -= 1

        if self._cycles_frame < self.VBLANK_CYCLES and not self._started_vblank:     # Este es el ciclo en el que entramos en VBLANK
                self.start_vblank()    # Activamos el período VBLANK al inicio del período

        # Cuando se termina el frame se hace todo ésto
        if self._end_frame:
            self._reg_status = 0        # reseteamos el registro de estado
            self._started_vblank = 0    # En el nuevo frame indicamos que no se ha procesado el período VBLANK aún

            # Dibujamos los sprites
            if self.control_2_sprites_bit_4():
                self.draw_sprites()

            if self.control_2_background_bit_3():
                self._reg_vram_addr = self._reg_vram_tmp     # Esto es así al principio de cada frame
                self._gfx.update()

            #Reseteamos la cache de tiles al principio del frame:
            self._tiles_cache = {}

            # Cargamos los sprites para el siguiente frame
            self.get_sprites_list()
            self._sprite_zero = self._sprites_list[0]
            (self._tile_sprite_zero_index_palette_0, self._tile_sprite_zero_rgb_0), (self._tile_sprite_zero_index_palette_1, self._tile_sprite_zero_rgb_1) = self._sprite_zero.get_tiles()

            self._sprite_hit = 0

            # Indicamos que ha finalizado el frame
            self._end_frame = False


    # Lee el registro indicado por su dirección en memoria
    def read_reg(self, addr):
        d = 0x00

        if addr == 0x2002:
            d = self.read_reg_2002()
        elif addr == 0x2004:
            d = self.read_reg_2004()
        elif addr == 0x2007:
            d = self.read_reg_2007()

        return d


    # Según el documento SKINNY.TXT
    def read_reg_2002(self):
        r = self._reg_status

        # Cuando se lee este registro se pone el flag de vblank a 0
        self._reg_status = nesutils.set_bit(r, 7, 0)

        self._reg_vram_switch = 0

        return r


    def read_reg_2004(self):
        addr = self._reg_spr_addr
        self._reg_spr_io = self._sprite_memory.read_data(addr)

        return self._reg_spr_io


    def read_reg_2007(self):
        addr = self._reg_vram_addr & 0x3FFF

        # Si la dirección es de la paleta se devuelve el valor inmediatamente, sino se retrasa a la siguiente lectura
        if addr >= 0x3F00:
            data = self._memory.read_data(self._reg_vram_addr - 0x1000)
            self._vram_buffer = data
        else:
            data = self._vram_buffer
            self._vram_buffer = self._memory.read_data(self._reg_vram_addr)

        self._reg_vram_io = data

        if self.control_1_increment_bit_2() == 0:
            self._reg_vram_addr = (self._reg_vram_addr + 1) & 0xFFFF
        else:
            self._reg_vram_addr = (self._reg_vram_addr + 32) & 0xFFFF

        return data


    # Escribe el registro indicado por su dirección en memoria
    def write_reg(self, data, addr):
        if addr == 0x2000:
            self.write_reg_2000(data)
        elif addr == 0x2001:
            self.write_reg_2001(data)
        elif addr == 0x2003:
            self.write_reg_2003(data)
        elif addr == 0x2004:
            self.write_reg_2004(data)
        elif addr == 0x2005:
            self.write_reg_2005(data)
        elif addr == 0x2006:
            self.write_reg_2006(data)
        elif addr == 0x2007:
            self.write_reg_2007(data)


    # Según el documento SKINNY.TXT
    def write_reg_2000(self, data):
        d = data & 0xFF
        self._reg_control_1 = d

        # Transfiere el valor de los bits 0-1 a los bits 10-11 del registro vram_tmp
        self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 10, d & 0x01)
        self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 11, d & 0x02)


    def write_reg_2001(self, data):
        self._reg_control_2 = data & 0xFF


    def write_reg_2003(self, data):
        self._reg_spr_addr = data & 0xFF


    def write_reg_2004(self, data):
        d = data & 0xFF
        self._reg_spr_io = d
        self._sprite_memory.write_data(d, self._reg_spr_addr)


    # Según el documento SKINNY.TXT
    def write_reg_2005(self, data):
        d = data & 0xFF

        # Primera escritura en $2005
        if self._reg_vram_switch == 0:
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 0, d & 0x08)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 1, d & 0x10)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 2, d & 0x20)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 3, d & 0x40)
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 4, d & 0x80)

            # FIXME: según NinTech.txt. No aparece en SKINNY.TXT
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 15, 0)

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

            # FIXME: según NinTech.txt. No aparece en SKINNY.TXT
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 15, 0)

            self._reg_vram_switch = 0


    # Según el documento SKINNY.TXT
    def write_reg_2006(self, data):
        d = data & 0xFF

        # Primera escritura en $2006
        if self._reg_vram_switch == 0:
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

            # FIXME: según NinTech.txt. No aparece en SKINNY.TXT
            self._reg_vram_tmp = nesutils.set_bit(self._reg_vram_tmp, 15, 0)

            self._reg_vram_addr = self._reg_vram_tmp

            self._reg_vram_switch = 0


    def write_reg_2007(self, data):
        d = data & 0xFF
        a = self._reg_vram_addr
        self._reg_vram_io = d
        self._memory.write_data(d, a)

        if self.control_1_increment_bit_2() == 0:
            self._reg_vram_addr = (self._reg_vram_addr + 1) & 0xFFFF
        else:
            self._reg_vram_addr = (self._reg_vram_addr + 32) & 0xFFFF


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
        self._reg_x_offset = (self._reg_x_offset + 1) & 0x07
        bit_10 = (r & 0x0400) >> 10
        bits_0_4 = r & 0x001F

        if self._reg_x_offset == 0:
            bits_0_4 = (bits_0_4 + 1) & 0x1F

            if bits_0_4 == 0x0:
                bit_10 = ~bit_10 & 0x1

        r = (r & 0xFBE0) | (bit_10 << 10) | bits_0_4

        self._reg_vram_addr = r


    def incr_yscroll(self):
        r = self._reg_vram_addr
        self._tmp_y_offset = (((r & 0x7000) >> 12) + 1) & 0x07
        bit_11 = (r & 0x0800) >> 11
        bits_5_9 = (r & 0x03E0) >> 5

        if self._tmp_y_offset == 0:
            bits_5_9 = (bits_5_9 + 1) % 30

            if bits_5_9 == 0x0:
                bit_11 = ~bit_11 & 0x1

        r = (r & 0x41F) | (self._tmp_y_offset << 12) | (bit_11 << 11) | (bits_5_9 << 5)

        self._reg_vram_addr = r


    # Devuelve el valor de 8 bits del registro de desplazamiento x del scroll de un tile
    def get_x_offset(self):
        return self._reg_x_offset


    # Devuelve el valor de 8 bits del registro de desplazamiento y del scroll de un tile
    def get_y_offset(self):
        return (self._reg_vram_addr & 0x7000) >> 12


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
        # Ponemos el bit 7 del registro de Status a 1, que indica que estamos en el período VBLANK
        self._reg_status = nesutils.set_bit(self._reg_status, 7, 1)

        # Activamos la interrupción si las NMI están activadas en el registro de control 1
        if self._reg_control_1 & 0x80:
            self._int_vblank = 1

        # Indicamos que ya hemos procesado el período VBLANK
        self._started_vblank = 1


    # Finaliza un período VBLANK
    def end_vblank(self):
        self._reg_status = 0
        self._started_vblank = 0


    # Devuelve si hay una solicitud de interrupción vblank
    def get_int_vblank(self):
        return self._int_vblank

    # Establece el valor de la solicitud de interrupción vblank
    def set_int_vblank(self, value):
        self._int_vblank = value

    # Establece el flag sprite hit del registro de status
    def set_sprite_hit(self, v):
        self._sprite_hit = v
        self._reg_status = nesutils.set_bit(self._reg_status, 6, v)

    # Indica si nos encontramos en un periodo VBLANK
    def is_vblank(self):
        return self._scanline_number > 240


    def draw_scanline(self):
        y = self._scanline_number - 1

        if self.control_2_background_bit_3():
            # Copia el desplazamiento X del registro tmp al addr al principio del scanline
            tmp = self._reg_vram_tmp

            # Copia los bits correspondientes del registro temporal al de dirección al principio
            # del scanline
            self._reg_vram_addr = (self._reg_vram_addr & 0b1111101111100000) | (tmp & 0x41F)

            # Pintamos el pixel
            x = 0
            while x < 256:
                self.draw_pixel(x, y)

                # Incrementamos el registro de dirección horizontalmente si estamos pintando el background
                self.incr_xscroll()

                # Si hemos dibujado el último pixel en anchura del "pattern", indicamos que hay que usar otro
                if self._reg_x_offset == 0:
                    self._fetch_pattern = True

                x += 1

            # Incrementamos el registro de dirección verticalmente si estamos pintando el background
            self.incr_yscroll()

        # Si aún no se ha producido, calculamos si ha habido impacto del Sprite zero con el fondo
        if not self._sprite_hit:
            self._calc_sprite_hit()


        # Cuando se termina de dibujar el scanline siempre hay que usar otro "pattern"
        self._fetch_pattern = True


    # Dibuja un pixel de la pantalla
    def draw_pixel(self, x, y):
        self.pixel_background[x][y] = 0

        # Dibuja el fondo
        pattern_pixel_x = self._reg_x_offset
        pattern_pixel_y = self._tmp_y_offset

        # Calcula la dirección en la Name Table activa
        name_table_addr = 0x2000 + (self._reg_vram_addr & 0x0FFF)

        if self._fetch_pattern:
            pattern_table_number = self.control_1_background_pattern_bit_4()
            pattern_index = self._memory.read_data(name_table_addr)

            attr_color = self.calc_attr_color(name_table_addr)

            if (pattern_table_number, pattern_index, attr_color) in self._tiles_cache:
                self._tile_bg_index_palette, self._tile_bg_rgb = self._tiles_cache[pattern_table_number, pattern_index, attr_color]
            else:
                self._tile_bg_index_palette, self._tile_bg_rgb = self.fetch_pattern(pattern_table_number, pattern_index, attr_color, PPUMemory.ADDR_IMAGE_PALETTE)
                self._tiles_cache[(pattern_table_number, pattern_index, attr_color)] = (self._tile_bg_index_palette, self._tile_bg_rgb)


            self._fetch_pattern = False

        # Desactivado el clipping por cuestiones de rendimiento
        #if self.control_2_clip_background_bit_1() or x >= 8:

        # Comprueba si el pixel actual es de background
        if self._tile_bg_index_palette[pattern_pixel_x][pattern_pixel_y] & 0x03:
            self.pixel_background[x][y] = 1

        self._gfx.draw_pixel(x, y, self._tile_bg_rgb[pattern_pixel_x][pattern_pixel_y])


    # Dibuja todos los sprites de la lista de sprites
    def draw_sprites(self):
        size_bit = self.control_1_sprites_size_bit_5()
        n = 0
        while n < 64:
            sprite = self._sprites_list[n]

            size_y = size_bit * 8 + 8

            for spr_x in range(8):
                for spr_y in range(size_y):
                    self.draw_sprite_pixel(sprite, spr_x, spr_y)

            n += 1


    # Dibuja el pixel (spr_x, spr_y) del sprite en pantalla en su posición correspondiente
    def draw_sprite_pixel(self, sprite, spr_x, spr_y):
        # Tamaño de los sprites
        size_bit = self.control_1_sprites_size_bit_5()

        off_x = sprite.get_offset_x()
        off_y = sprite.get_offset_y()

        screen_x = off_x + spr_x
        screen_y = off_y + spr_y

        if screen_x < 256 and screen_y < 240:
            pixel_background = self.pixel_background[screen_x][screen_y]
            # Si los sprites son 8x8
            if size_bit == 0:
                # Obtenemos el tile
                self._tile_sprite_index_palette, self._tile_sprite_rgb = sprite.get_tiles()[0]

                # Si está activado el flag de invertir horizontalmente
                if sprite.get_horizontal_flip():
                    spr_x = 7 - spr_x

                # Si está activado el flag de invertir verticalmente
                if sprite.get_vertical_flip():
                    spr_y = 7 - spr_y
            # Si los sprites son 8x16
            else:
                vertical_flip = sprite.get_vertical_flip()

                # Obtenemos los tiles
                if spr_y < 8:
                    self._tile_sprite_index_palette, self._tile_sprite_rgb = sprite.get_tiles()[vertical_flip]
                else:
                    self._tile_sprite_index_palette, self._tile_sprite_rgb = sprite.get_tiles()[not vertical_flip]
                    spr_y = spr_y & 0x07

                # Si está activado el flag de invertir horizontalmente
                if sprite.get_horizontal_flip():
                    spr_x = 7 - spr_x

                # Si está activado el flag de invertir verticalmente
                if vertical_flip:
                    spr_y = 7 - spr_y

            # Si el pixel del sprite no es vacío
            transparent = not (self._tile_sprite_index_palette[spr_x][spr_y] & 0x03)
            if not transparent:
                # Pinta el pixel si tiene prioridad sobre las nametables, o en caso contrario si el color de fondo es transparente
                if (pixel_background != 2) and (sprite.get_priority() == 0 or not pixel_background):
                    self._gfx.draw_pixel(screen_x, screen_y, self._tile_sprite_rgb[spr_x][spr_y])

                self.pixel_background[screen_x][screen_y] = 2


    # Devuelve una lista de objetos de clase Sprite con los sprites de la memoria de sprites
    def get_sprites_list(self):
        n = 0
        addr = 0x00

        while n < 64:
            self._sprites_list[n].load_by_addr(self._sprite_memory, addr)
            addr += 0x04
            n += 1


    def _calc_sprite_hit(self):
        sprites_size_bit = self.control_1_sprites_size_bit_5()
        if self._sprite_zero.is_in_scanline(self._scanline_number, sprites_size_bit):
            y = self._scanline_number - 1
            offset_x = self._sprite_zero.get_offset_x()
            spr_y = y - self._sprite_zero.get_offset_y()

            # Obtiene el tile del Sprite y su posición vertical
            tile_sprite_zero_index_palette, tile_sprite_zero_rgb = self._sprite_zero.get_tiles()[sprites_size_bit]
            spr_y = spr_y & 0x07

            # Calcula si hay alguna colisión
            for spr_x in range(8):
                screen_x = offset_x + spr_x
                if screen_x < 255:
                    if (tile_sprite_zero_index_palette[spr_x][spr_y] & 0x03 != 0) and (self.pixel_background[screen_x][y] == 1):
                        self.set_sprite_hit(1)


    # Devuelve el color almacenado en la attr table para el tile de una dirección de la name table
    def calc_attr_color(self, name_table_addr):
        # La posición de la name table en la que está el tile
        pos = name_table_addr & 0x03FF

        # Posición del grupo de 8x8 tiles que contiene el tile con el que estamos trabajando
        group_x = (pos >> 2) & 0x07
        group_y = (pos >> 7) & 0x07

        # Posición del byte en la "attr table" correspondiente al grupo 8x8
        attr_pos = (group_y * 8) + group_x

        # Dirección de memoria de la "attr table"
        attr_addr = (name_table_addr & 0xFC00)  | (0x03C0 + attr_pos)

        # Byte leído de la attr table que contiene la info de color
        attr_data = self._memory.read_data(attr_addr)

        # Calculamos la posición relativa del tile dentro del grupo 8x8
        # La posición x dentro del grupo 4x4 la dan los 2 bits menos significativos de la posición del tile en la name table
        pos_x = pos & 0x03

        # La posición y dentro del grupo 4x4 la dan los bits 5 y 6 de la posición del tile en la name table
        pos_y = (pos >> 5) & 0x03

        # Calcula el area que le corresponde al tile dentro del grupo 4x4
        attr_area = (pos_y & 0x02) | (pos_x >> 1)

        color = (attr_data >> (attr_area << 1)) & 0x03

        return color


    # Lee el patrón "pattern_index" de la tabla de patrones "pattern_table" con el color "attr_color" y la paleta
    # de colores ubicada en la dirección de memoria "palette_addr" y lo coloca en las variables de salida
    # "tile_palette_index" y "tile_rgb"
    def fetch_pattern(self, pattern_table, pattern_index, attr_color, palette_addr):
        tile_palette_index = [None] * 8
        for x in xrange(8):
            tile_palette_index[x] = [0] * 8

        tile_rgb = [None] * 8
        for x in xrange(8):
            tile_rgb[x] = [(0, 0, 0)] * 8

        if pattern_table == 0:
            addr = 0x0000
        else:
            addr = 0x1000

        addr = addr + pattern_index * 16

        y = 0
        # Lee los bytes del patrón de memoria y lo guarda en una lista
        for a in xrange(addr, addr + 8):
            byte_1 = self._memory.read_data(a)
            byte_2 = self._memory.read_data(a + 8)

            for x in xrange(8):
                # Calcula la dirección del color en la paleta de memoria y lo extrae de la tabla de colores
                palette_index = (0x00 | ((byte_1 & (0x01 << x)) >> x) | (((byte_2 & (0x01 << x)) >> x) << 1) | ((attr_color & 0x03) << 2))

                # Asigna el índice de la paleta a la posición correspondiente:
                tile_palette_index[7 - x][y] = palette_index

                color_index = self._memory.read_data(palette_addr + palette_index) & 0x3F
                rgb = self.get_color(color_index)
                tile_rgb[7 - x][y] = rgb

            y = (y + 1) & 0x07

        return (tile_palette_index, tile_rgb)


    def get_color(self, index):
        return PPU._COLOR_PALETTE[index & 0x3F]


    # Borra la cache de Tiles
    def reset_tiles_cache(self):
        self._tiles_cache = {}


    #######################################################################
    # Variables de clase
    #######################################################################
    # Paleta de colores:
    _COLOR_PALETTE = [(0x75, 0x75, 0x75),    #0x00
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





