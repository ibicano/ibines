# -*- coding: utf-8 -*-

import Mapper

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


    # Método de clase que devuelve un objeto del mapper indicado
    @classmethod
    def instance_mapper(cls, mapper_code, rom):
        if mapper_code == 0:
            return NROM(rom)
        elif mapper_code == 1:
            return MMC1(rom)
        elif mapper_code == 3:
            return CNROM(rom)
        elif mapper_code == 4:
            return MMC3(rom)


class NROM(Mapper):

    MAPPER_CODE = 0

    def __init__(self, rom):
        super(NROM, self).__init__(rom)

        #Carga los bancos
        self._prg_rom_0 = [0x00] * 16384
        self._prg_rom_1 = [0x00] * 16384

        if self._rom.get_prg_count() == 1:
            self._prg_rom_0 = self._rom.get_prg(0)
        elif self._rom.get_prg_count() == 2:
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
            if self._rom.get_prg_count() == 1:
                d = self._prg_rom_0[a]
            elif self._rom.get_prg_count() == 2:
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
        self._chr_0 = None         # 0x0000
        self._chr_1 = None         # 0x1000

        # Bancos de PGR de 16K
        self._prg_0 = None        # 0x8000
        self._prg_1 = None        # 0xC000

        # Se carga el estado inicial
        self._prg_0 = self._rom.get_prg(0)
        self._prg_1 = self._rom.get_prg(self._rom.get_prg_count() - 1)


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
            self._shift_reg = self._shift_reg | ((d & 0x01) << 4)

            if self._counter == 4:
                if self._addr_13_14 == 0x0000:
                    self._reg0 = self._shift_reg
                elif self._addr_13_14 == 0x2000:
                    self._reg1 = self._shift_reg
                elif self._addr_13_14 == 0x4000:
                    self._reg2 = self._shift_reg
                elif self._addr_13_14 == 0x6000:
                    # Si el tamaño de página es de 16K
                    if (self._reg0 & 0x08) >> 3:
                        self._reg3 = self._shift_reg
                    # Si el tamaño de página es de 32k hay que desplazar un bit a la izquierda, ya que el 0 se ignora
                    else:
                        self._reg3 = self._shift_reg << 1

                self._swap_banks()

                self._shift_reg = 0x00
                self._counter = 0
            else:
                self._shift_reg >>= 1
                self._counter += 1


    def mirror_mode(self):
        # Si el bit 1 del registro 0 es 0 se activa single mirroring (valor 2)
        if self._reg0 & 0x02 == 0:
            return 2
        # Si el bit 1 es 1 el bit 0 indica el tipo. 0: vertical; 1: horizontal
        else:
            return (~self._reg0) & 0x01

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
        # Bancos de 4k
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
            bank_number_16k_0 = bank_number
            bank_number_16k_1 = bank_number + 1

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


# TODO: terminar de implementar el mapper MMC3
class MMC3(Mapper):

    MAPPER_CODE = 4

    def __init__(self, rom):
        super(MMC3, self).__init__(rom)

        # CPU
        self._cpu = None

        # Bancos prg de 8k
        self._prg_rom_0 = [0x00] * 8192
        self._prg_rom_1 = [0x00] * 8192
        self._prg_rom_2 = [0x00] * 8192
        self._prg_rom_3 = [0x00] * 8192

        # Bancos chr de 1k
        self._chr_rom_0 = self._rom.get_chr_1k(0)
        self._chr_rom_1 = self._rom.get_chr_1k(1)
        self._chr_rom_2 = self._rom.get_chr_1k(2)
        self._chr_rom_3 = self._rom.get_chr_1k(3)
        self._chr_rom_4 = self._rom.get_chr_1k(4)
        self._chr_rom_5 = self._rom.get_chr_1k(5)
        self._chr_rom_6 = self._rom.get_chr_1k(6)
        self._chr_rom_7 = self._rom.get_chr_1k(7)

        # Modo mirror
        self._mirror_mode = 0

        # Estado de save RAM
        self._save_ram = 0

        # Banco seleccionado
        self._bank_select = 0

        # Modo de swap
        self._bank_mode = 0

        # Indica si se debe hacer XOR 0x1000 cuando bank_select es 0-5
        self._bank_inversion = 0

        self._prg_count_8k = self._rom.get_prg_count() * 2

        # Iniciamos el banco correspondiente a las posiciones 0xE000-0xFFFF que es fijo siempre
        self._prg_rom_3 = self._rom.get_prg_8k(self._prg_count_8k - 1)

        # Registros de datos
        self._r0 = 0
        self._r1 = 0
        self._r2 = 0
        self._r3 = 0
        self._r4 = 0
        self._r5 = 0
        self._r6 = 0
        self._r7 = 0

        # Rregistro relacionados con las IRQ
        self._irq_enable = 0
        self._irq_reload_flag = 0       # Indica si se recarga el irq_counter con irq_latch
        self._irq_latch = 0             # Valor con el que recargar el irq_counter
        self._irq_counter = 0           # Contador de scanlines que va decrementándose y cuando llega a 0 lanza una IRQ


    def mirror_mode(self):
        return self._mirror_mode


    def set_cpu(self, cpu):
        self._cpu = cpu


    def read_prg(self, addr):
        data = 0x0
        a = addr % 0x2000

        if 0x8000 <= addr <= 0x9FFF:
            data = self._prg_rom_0[a]
        elif 0xA000 <= addr <= 0xBFFF:
            data = self._prg_rom_1[a]
        elif 0xC000 <= addr <= 0xDFFF:
            data = self._prg_rom_2[a]
        elif 0xE000 <= addr <= 0xFFFF:
            data = self._prg_rom_3[a]

        return data


    def read_chr(self, addr):
        data = 0x0
        a = addr % 0x400

        if 0x0000 <= addr <= 0x03FF:
            data = self._chr_rom_0[a]
        elif 0x0400 <= addr <= 0x07FF:
            data = self._chr_rom_1[a]
        elif 0x0800 <= addr <= 0x0BFF:
            data = self._chr_rom_2[a]
        elif 0x0C00 <= addr <= 0x0FFF:
            data = self._chr_rom_3[a]
        elif 0x1000 <= addr <= 0x13FF:
            data = self._chr_rom_4[a]
        elif 0x1400 <= addr <= 0x17FF:
            data = self._chr_rom_5[a]
        elif 0x1800 <= addr <= 0x1BFF:
            data = self._chr_rom_6[a]
        elif 0x1C00 <= addr <= 0x1FFF:
            data = self._chr_rom_7[a]

        return data


    def write_prg(self, data, addr):
        if (not addr & 0x01) and (0x8000 <= addr < 0xA000):
            self._bank_select = data & 0x07
            self._bank_mode = (data & 0x40) >> 6
            self._bank_inversion = (data & 0x80) >> 7
        elif (addr & 0x01) and (0x8000 <= addr < 0xA000):
            if self._bank_select == 0:
                self._r0 = data
            elif self._bank_select == 1:
                self._r1 = data
            elif self._bank_select == 2:
                self._r2 = data
            elif self._bank_select == 3:
                self._r3 = data
            elif self._bank_select == 4:
                self._r4 = data
            elif self._bank_select == 5:
                self._r5 = data
            elif self._bank_select == 6:
                self._r6 = data
            elif self._bank_select == 7:
                self._r7 = data
        elif (not addr & 0x01) and (0xA000 <= addr < 0xC000):
            self._mirror_mode = data & 0x01
        elif (addr & 0x01) and (0xA000 <= addr < 0xC000):
            self._save_ram = (data & 0xC0) >> 6
        # IRQs
        elif (not addr & 0x01) and (0xC000 <= addr <= 0xDFFF):
            self._irq_latch = data
        elif (addr & 0x01) and (0xC000 <= addr <= 0xDFFF):
            self._irq_reload_flag = 1
        elif (not addr & 0x01) and (0xE000 <= addr <= 0xFFFF):
            self._irq_enable = 0
        elif (addr & 0x01) and (0xE000 <= addr <= 0xFFFF):
            self._irq_enable = 1

        self._swap_banks()


    def _swap_banks(self):
        # Bancos CHR
        if self._bank_inversion == 0:
            self._chr_rom_0 = self._rom.get_chr_1k(self._r0 & 0xFE)
            self._chr_rom_1 = self._rom.get_chr_1k(self._r0 | 0x01)

            self._chr_rom_2 = self._rom.get_chr_1k(self._r1 & 0xFE)
            self._chr_rom_3 = self._rom.get_chr_1k(self._r1 | 0x01)

            self._chr_rom_4 = self._rom.get_chr_1k(self._r2)

            self._chr_rom_5 = self._rom.get_chr_1k(self._r3)

            self._chr_rom_6 = self._rom.get_chr_1k(self._r4)

            self._chr_rom_7 = self._rom.get_chr_1k(self._r5)
        else:
            self._chr_rom_4 = self._rom.get_chr_1k(self._r0 & 0xFE)
            self._chr_rom_5 = self._rom.get_chr_1k(self._r0 | 0x01)

            self._chr_rom_6 = self._rom.get_chr_1k(self._r1 & 0xFE)
            self._chr_rom_7 = self._rom.get_chr_1k(self._r1 | 0x01)

            self._chr_rom_0 = self._rom.get_chr_1k(self._r2)

            self._chr_rom_1 = self._rom.get_chr_1k(self._r3)

            self._chr_rom_2 = self._rom.get_chr_1k(self._r4)

            self._chr_rom_3 = self._rom.get_chr_1k(self._r5)


        # Bancos PRG
        if self._bank_mode == 0:
            self._prg_rom_0 = self._rom.get_prg_8k(self._r6)
            self._prg_rom_2 = self._rom.get_prg_8k(self._prg_count_8k - 2)
        elif self._bank_mode == 1:
            self._prg_rom_0 = self._rom.get_prg_8k(self._prg_count_8k - 2)
            self._prg_rom_2 = self._rom.get_prg_8k(self._r6)

        self._prg_rom_1 = self._rom.get_prg_8k(self._r7)


    def scanline_tick(self):
        if self._irq_counter == 0:
            if self._irq_enable:
                self._cpu.set_irq(1)
            self._irq_counter = self._irq_latch
        else:
            self._irq_counter -= 1
            if self._irq_reload_flag:
                self._irq_counter = self._irq_latch














