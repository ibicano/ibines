import Mapper

class Mapper(object):

    def __init__(self, rom):
        super(Mapper, self).__init__()

        # Almacena la ROM del juego
        self._rom = rom

    def read_chr(self,addr):
        pass

    def write_chr(self,addr):
        pass

    def read_prg(self,addr):
        pass

    def write_prg(self, data, addr):
        pass


    # 0x0: horizontal; 0x1: vertical: 0x2: single; 0x3: 4-screen
    def mirror_mode(self):
        pass


    def get_prg_count(self):
        return self._rom.get_pgr_count()


    def get_chr_count(self):
        return self._rom.get_chr_count()


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
        self._prg_rom_0 = [0x00] * 16384
        self._prg_rom_1 = [0x00] * 16384

        if self._rom.get_pgr_count() == 1:
            self._prg_rom_0 = self._rom.get_prg(0)
        elif self._rom.get_pgr_count() == 2:
            self._prg_rom_0 = self._rom.get_prg(0)
            self._prg_rom_1 = self._rom.get_prg(1)

        self._chr_rom_0 = [0x00] * 8192
        self._chr_rom_1 = [0x00] * 8192

        if self._rom.get_chr_count() == 1:
            self._chr_rom_0 = self._rom.get_chr(0)
        elif self._rom.get_chr_count() == 2:
            self._chr_rom_0 = self._rom.get_chr(0)
            self._chr_rom_1 = self._rom.get_chr(1)


    def read_chr(self, addr):
        a = addr % 0x4000
        d = 0x00
        if 0x0000 <= a < 0x2000:
            d = self._chr_rom_0[a]

        return d


    def read_prg(self, addr):
        d = 0x00

        if 0x8000 <= addr < 0xC000:
            a = (addr - 0x8000) % 0x4000
            d = self._prg_rom_0[a]
        elif 0xC000 <= addr < 0x10000:
            a = (addr - 0x8000) % 0x4000
            if self._rom.get_pgr_count() == 1:
                d = self._prg_rom_0[a]
            elif self._rom.get_pgr_count() == 2:
                d = self._prg_rom_1[a]

        return d


    def mirror_mode(self):
        return self._rom.get_mirroring()


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

        # Memoria CHR RAM (si la tuviera. Sólo en caso que los bancos CHR-ROM sean 0)
        self._chr_ram_0 = [0x00] * 4096
        self._chr_ram_1 = [0x00] * 4096

        # Bancos de memoria

        # Bancos de CHR de 4K
        self._chr_0 = [0x00] * 4096         # 0x0000
        self._chr_1 = [0x00] * 4096         # 0x1000

        # Bancos de PGR de 16K
        self._prg_0 = [0x00] * 16384        # 0x8000
        self._prg_1 = [0x00] * 16384        # 0xC000

        # Se carga el estado inicial
        self._prg_0 = self._rom.get_prg(0)
        self._prg_1 = self._rom.get_prg(self._rom.get_pgr_count() - 1)


    def read_chr(self, addr):
        a = addr % 0x4000
        d = 0x00

        if 0x0000 <= a <= 0x0FFF:
            d = self._chr_0[a]
        elif 0x1000 <= a <= 0x1FFF:
            d = self._chr_1[a - 0x1000]

        return d


    def read_prg(self, addr):
        d = 0x00

        if 0x8000 <= addr <= 0xBFFF:
            d = self._prg_0[addr - 0x8000]
        elif 0xC000 <= addr <= 0xFFFF:
            d = self._prg_1[addr - 0xC000]

        return d


    def write_chr(self, data, addr):
        if self._rom.get_chr_count() == 0:
            a = addr % 0x4000
            d = data & 0xFF

            if 0x0000 <= a <= 0x0FFF:
                self._chr_0[a] = d
            elif 0x1000 <= a <= 0x1FFF:
                self._chr_1[a - 0x1000] = d


    # Escribe en los registros. 1 bit cada vez ya que es una linea serie
    def write_prg(self, data, addr):
        d = data & 0xFF

        # Si estamos en el primer ciclo copiamos los bits 13 y 14 de la dirección al registro de dirección
        if self._counter == 0:
            self._addr_13_14 = addr & 0x6000

        # Si el bit 7 del dato es 1 o la dirección es de otro registro se resetea
        if (d & 0x80) or (addr & 0x6000 != self._addr_13_14):
            self._shift_reg = 0x00
            self._counter = 0
        else:
            self._shift_reg = self._shift_reg | (d & 0x10)

            if self._counter == 4:
                if self._addr_13_14 == 0x0000:
                    self._reg0 = self._shift_reg
                elif self._addr_13_14 == 0x2000:
                    self._reg1 = self._shift_reg
                elif self._addr_13_14 == 0x4000:
                    self._reg2 = self._shift_reg
                elif self._addr_13_14 == 0x6000:
                    self._reg3 = self._shift_reg

                self._swap_banks()

                self._shift_reg = 0x00
                self._counter = 0
            else:
                self._shift_reg >>= 1
                self._counter += 1


    def mirror_mode(self):
        # Si el bit 2 del registro 0 es 0 se activa single mirroring (valor 2)
        if self._reg0 & 0x02 == 0:
            return 2
        else:
            return self._reg0 & 0x01


    def get_reg0(self):
        return self._reg0


    def get_reg1(self):
        return self._reg1

    def get_reg2(self):
        return self._reg2

    def get_reg3(self):
        return self._reg3


    # Intercambia los bancos de memoria en función del valor de los registros
    def _swap_banks(self):
        # Intercambio de bancos CHR
        chr_size = (self._reg0 & 0x10) >> 4                # 0: bancos de 8k; 1: bancos de 4k
        bank_number_0000 = self._reg1 & 0x0F               # Número de banco para cargar en 0x0000
        bank_number_1000 = self._reg2 & 0x0F               # Número de banco para cargar en 0x1000 (Si son de 4k)

        # Bancos de 8k
        if chr_size == 0:
            # Si tiene CHR-RAM se intercambia la RAM
            if self._rom.get_chr_count() == 0:
                self._chr_0 = self._chr_ram_0
                self._chr_1 = self._chr_ram_1
            # Si no se intercambia la ROM
            else:
                self._chr_0 = self._rom.get_chr(bank_number_0000 >> 1)[0x0000:0x1000]
                self._chr_1 = self._rom.get_chr(bank_number_0000 >> 1)[0x1000:0x2000]
        # Bancos de 8k
        elif chr_size == 1:
            # Si son bancos de RAM
            if self._rom.get_chr_count() == 0:
                if bank_number_0000 == 0:
                    self._chr_0 = self._chr_ram_0
                elif bank_number_0000 == 1:
                    self._chr_0 = self._chr_ram_1

                if bank_number_1000 == 0:
                    self._chr_1 = self._chr_ram_0
                elif bank_number_1000 == 1:
                    self._chr_1 = self._chr_ram_1
            else:
                self._chr_0 = self._rom.get_chr_4k(bank_number_0000)
                self._chr_1 = self._rom.get_chr_4k(bank_number_1000)

        # Intercambio de bancos PRG
        prg_swap = (self._reg0 & 0x04) >> 2         # Dirección que cargar (sólo para bancos de 16k); 0: 0xC000; 1: 0x8000
        prg_size = (self._reg0 & 0x08) >> 3         # 0: bancos de 32k; 1: bancos de 16k
        bank_number = (self._reg3 & 0x0F)           # Número del banco a cargar

        # Si el tamaño del banco es de 32k
        if prg_size == 0:
            bank_number_16k_0 = bank_number >> 1
            bank_number_16k_1 = (bank_number >> 1) + 1

            self._prg_0 = self._rom.get_prg(bank_number_16k_0)
            self._prg_1 = self._rom.get_prg(bank_number_16k_1)
        # Si el tamaño del banco es de 16k
        elif prg_size == 1:
            # Se intercambia el banco 0xC000
            if prg_swap == 0:
                self._prg_1 = self._rom.get_prg(bank_number)
            # Se intercambia el banco 0x8000
            elif prg_swap == 0:
                self._prg_0 = self._rom.get_prg(bank_number)







