# -*- coding: utf-8 -*-


class Mapper(object):

    def __init__(self, rom):
        super(Mapper, self).__init__()

        # Almacena la ROM del juego
        self._rom = rom

    def read_chr(self, addr):
        pass

    def write_chr(self, addr):
        pass

    def read_prg(self, addr):
        pass

    def write_prg(self, data, addr):
        pass


    # 0x0: horizontal; 0x1: vertical: 0x2: single; 0x3: 4-screen
    def mirror_mode(self):
        pass


    def get_prg_count(self):
        return self._rom.get_prg_count()


    def get_chr_count(self):
        return self._rom.get_chr_count()


    # Este método es llamado cada vez que se finaliza un scanline
    def scanline_tick(self):
        pass





















