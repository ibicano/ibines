# -*- coding: utf-8 -*-

from Mapper import Mapper


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
        a = addr & 0x1FFF

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
        a = addr & 0x03FF

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
            self._mirror_mode = (~data) & 0x01
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
                self._irq_reload_flag = 0
