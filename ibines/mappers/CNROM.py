# -*- coding: utf-8 -*-

from Mapper import Mapper


class CNROM(Mapper):

    MAPPER_CODE = 3

    def __init__(self, rom):
        super(CNROM, self).__init__(rom)

        #Carga los bancos
        self._prg_rom_0 = [0x00] * 16384
        self._prg_rom_1 = [0x00] * 16384

        if self._rom.get_prg_count() == 1:
            self._prg_rom_0 = self._rom.get_prg(0)
        elif self._rom.get_prg_count() == 2:
            self._prg_rom_0 = self._rom.get_prg(0)
            self._prg_rom_1 = self._rom.get_prg(1)

        self._chr_rom = self._rom.get_chr(0)


    def read_chr(self, addr):
        a = addr % 0x4000
        d = 0x00
        if 0x0000 <= a < 0x2000:
            d = self._chr_rom[a]

        return d


    def read_prg(self, addr):
        d = 0x00

        if 0x8000 <= addr < 0xC000:
            a = (addr - 0x8000) % 0x4000
            d = self._prg_rom_0[a]
        elif 0xC000 <= addr < 0x10000:
            a = (addr - 0x8000) % 0x4000
            if self._rom.get_prg_count() == 1:
                d = self._prg_rom_0[a]
            elif self._rom.get_prg_count() == 2:
                d = self._prg_rom_1[a]

        return d


    def write_prg(self, data, addr):
        self._chr_rom = self._rom.get_chr(data & 0x03)


    def mirror_mode(self):
        return self._rom.get_mirroring()
