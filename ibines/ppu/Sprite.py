# -*- coding: utf-8 -*-

from PPUMemory import PPUMemory

# Clase que implmenta la info de un sprite de la ram de sprites
class Sprite(object):

    def __init__(self, ppu):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._offset_y = 0x00
        self._index = 0x00
        self._attributes = 0x00
        self._offset_x = 0x00
        self.sprite_zero = False

        self._ppu = ppu

        # Estos sólo se usan de forma temporal si los srpites son de 16 bits
        self._tile_sprite_index_0 = [None] * 8
        for x in range(8):
            self._tile_sprite_index_0[x] = [0] * 8

        self._tile_sprite_index_1 = [None] * 8
        for x in range(8):
            self._tile_sprite_index_1[x] = [0] * 8

        self._tile_sprite_rgb_0 = [None] * 8
        for x in range(8):
            self._tile_sprite_rgb_0[x] = [(0, 0, 0)] * 8

        self._tile_sprite_rgb_1 = [None] * 8
        for x in range(8):
            self._tile_sprite_rgb_1[x] = [(0, 0, 0)] * 8

        #######################################################################


    def load_by_addr(self, sprite_memory, sprite_addr):
        self._offset_y = sprite_memory.read_data(sprite_addr) + 1
        self._index = sprite_memory.read_data(sprite_addr + 1)
        self._attributes = sprite_memory.read_data(sprite_addr + 2)
        self._offset_x = sprite_memory.read_data(sprite_addr + 3)

        if sprite_addr == 0x00:
            self.sprite_zero = True
        else:
            self.sprite_zero = False

        # TODO: hay que implementar que cuando está el flipping activado lo aplique a los tiles
        # Cargamos los tiles de la memoria de la PPU
        size_bit = self._ppu.control_1_sprites_size_bit_5()
        if size_bit == 0:
            pattern_table = self._ppu.control_1_sprites_pattern_bit_3()

            # Obtenemos el tile
            self._tile_sprite_index_0, self._tile_sprite_rgb_0 = self._ppu.fetch_pattern(pattern_table, self.get_index(), self.get_attr_color(), PPUMemory.ADDR_SPRITE_PALETTE)

        # Si los sprites son 8x16
        else:
            pattern_table = self._index & 0x01
            index = self._index & 0xFE

            # Obtenemos los tiles
            self._tile_sprite_index_0, self._tile_sprite_rgb_0 = self._ppu.fetch_pattern(pattern_table, index, self.get_attr_color(), PPUMemory.ADDR_SPRITE_PALETTE)
            self._tile_sprite_index_1, self._tile_sprite_rgb_1 = self._ppu.fetch_pattern(pattern_table, index + 1, self.get_attr_color(), PPUMemory.ADDR_SPRITE_PALETTE)


    def get_tiles(self):
        return (self._tile_sprite_index_0, self._tile_sprite_rgb_0), (self._tile_sprite_index_1, self._tile_sprite_rgb_1)


    def load_by_number(self, sprite_memory, sprite_number):
        sprite_addr = sprite_number * 4
        self.load_by_addr(sprite_memory, sprite_addr)


    def get_offset_x(self):
        return self._offset_x


    def get_offset_y(self):
        return self._offset_y


    def get_index(self):
        return self._index

    # Indica si el sprite aparece en el pixel de pantalla indicado
    def is_in(self, x, y, size_bit):
        size_y = size_bit * 8 + 8

        return ((x >= self._offset_x and x < self._offset_x + 8) and (y >= self._offset_y and y < self._offset_y + size_y))


    def is_in_scanline(self, scanline, size_bit):
        size_y = size_bit * 8 + 8

        y = scanline - 1

        return (self._offset_y <= y < (self._offset_y + size_y))


    # Devuelve atributos:
    def get_attr_color(self):
        return self._attributes & 0x03

    def get_priority(self):
        return (self._attributes & 0x20) >> 5

    def get_horizontal_flip(self):
        return (self._attributes & 0x40) >> 6

    def get_vertical_flip(self):
        return (self._attributes & 0x80) >> 7