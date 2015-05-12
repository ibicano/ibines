import Mapper

class Mapper(object):

    def __init__(self, rom):
        super(Mapper, self).__init__()

        # Almacena la ROM del juego
        self._rom = rom

    def read(self,addr):
        pass

    def write(self, data, addr):
        pass


    # Método de clase que devuelve un objeto del mapper indicado
    @classmethod
    def instance_mapper(cls, mapper_code, rom):
        if mapper_code == 0:
            return NROM(rom)
        elif mapper_code == 1:
            return MMC1(rom)


class NROM(Mapper):

    MAPPER_CODE = 0

    def __init__(self, rom):
        super(NROM, self).__init__(rom)

        #Carga los bancos
        self._pgr_rom_0 = [0x00] * 16384
        self._pgr_rom_1 = [0x00] * 16384

        if self._rom.get_pgr_count() == 1:
            self._pgr_rom_0 = self._rom.get_pgr(0)
        elif self._rom.get_pgr_count() == 2:
            self._pgr_rom_0 = self._rom.get_pgr(0)
            self._pgr_rom_1 = self._rom.get_pgr(1)

        self._chr_rom_0 = [0x00] * 8192
        self._chr_rom_1 = [0x00] * 8192

        if self._rom.get_chr_count() == 1:
            self._chr_rom_0 = self._rom.get_chr(0)
        elif self._rom.get_chr_count() == 2:
            self._chr_rom_0 = self._rom.get_chr(0)
            self._chr_rom_1 = self._rom.get_chr(1)


    def read(self,addr):
        a = (addr - 0x8000) % 0x4000
        d = 0x00

        if 0x8000 <= addr < 0xC000:
            d = self._pgr_rom_0[a]
        elif 0xC000 <= addr < 0x10000:
            if self._rom.get_pgr_count() == 1:
                d = self._pgr_rom_0[a]
            elif self._rom.get_pgr_count() == 2:
                d = self._pgr_rom_1[a]

        return d


class MMC1(Mapper):

    MAPPER_CODE = 1

    def __init__(self, rom):
        super(MMC1, self).__init__(rom)

        # Registros
        self._shift_reg = 0x00

        self._reg0 = 0x00
        self._reg1 = 0x00
        self._reg2 = 0x00
        self._reg3 = 0x00

        # Contador de escritura
        self._addr_13_14 = 0x0000
        self._counter = 0


        # Bancos de memoria


    # Escribe en los registros (1 bit cada vez, ya que es una línea serie)
    def write(self, data, addr):
        d = 0xFF

        # Si estamos en el primer ciclo copiamos los bits 13 y 14 de la dirección al registro de dirección
        if self._counter == 0:
            self._addr_13_14 = addr & 0x6000

        # Si el bit 7 del dato es 1 o la dirección es de otro registro se resetea
        if (d & 0x80) or (addr & 0x6000 != self._addr_13_14):
            self._shift_reg = 0x00
            self._counter = 0
        else:
            self._shift_reg = self._shift_reg | (d & 0x01)
            self._shift_reg <<= 1
            self._counter += 1

            if self._counter == 4:
                if self._addr_13_14 == 0x0000:
                    self._reg0 = self._shift_reg
                elif self._addr_13_14 == 0x2000:
                    self._reg1 = self._shift_reg
                elif self._addr_13_14 == 0x4000:
                    self._reg2 = self._shift_reg
                elif self._addr_13_14 == 0x6000:
                    self._reg3 = self._shift_reg

                self._shift_reg = 0x00
                self._counter = 0


    def get_reg0(self):
        return self._reg0


    def get_reg1(self):
        return self._reg1

    def get_reg2(self):
        return self._reg2

    def get_reg3(self):
        return self._reg3
