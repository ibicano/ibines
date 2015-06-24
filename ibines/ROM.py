# -*- coding: utf-8 -*-

# Clase que implementa la estructura de la ROM de un juego
# TODO: empollarse e implementar los mappers
class ROM(object):
    PGR_SIZE = 16384
    CHR_SIZE = 8192

    def __init__(self, file_name):
        ###########################################################################
        # Variables de instancia
        ###########################################################################
        self._rom = None            # Los bytes de la ROM en forma de lista

        self._prg_count = 0
        self._chr_count = 0
        self._rom_control_1 = 0x00
        self._rom_control_2 = 0x00
        self._ram_count = 0
        self._reserved = [0x00] * 7

        # Guarda si la ROM ha cargado correctamente
        self._load_ok = False
        ###########################################################################
        ###########################################################################

        self.load_file(file_name)


    def load_file(self, file_name):
        f = open(file_name, 'r')
        self._rom = bytearray(f.read())
        f.close()

        # Comprueba que el formato de la cabecera sea correcto
        if (str(self._rom[0:3]) == "NES") and self._rom[3] == 0x1A:
            # Carga la cabecera
            self._prg_count = self._rom[4]
            self._chr_count = self._rom[5]
            self._rom_control_1 = self._rom[6]
            self._rom_control_2 = self._rom[7]
            self._ram_count = self._rom[8]
            self._reserved = self._rom[9:16]

            # Reserva la memoria para almacenar los bancos en función del número de estos
            self._prg_banks = [None] * self._prg_count
            self._chr_banks = [None] * self._chr_count
            self._ram_banks = [None] * self._ram_count

            # Mirroring
            if self.get_control_1_mirroring_bit_3() == 0:
                self._mirroring = self.get_control_1_mirroring_bit_0()
            else:
                self._mirroring = 0x03

            # Ahora carga la info. La variable i es el índice de lectura de la posición de la ROM
            i = 16      # Empezamos después de la cabecera

            # Si hay un trainer lo carga primero
            if self.get_control_1_trainer_bit_2():
                self._trainer = self._rom[i:i + 512]
                i += 512

            # Carga los bancos PRG
            for n in range(self._prg_count):
                self._prg_banks[n] = self._rom[i:i + 16384]
                i += 16384

            # Carga los bancos CHR
            for n in range(self._chr_count):
                self._chr_banks[n] = self._rom[i:i + 8192]
                i += 8192

            self._load_ok = True
        else:
            self._load_ok = False
            print "Formato de fichero incorrecto"


    # Devuelve si la ROM ha cargado correctamente
    def get_load_ok(self):
        return self._load_ok


    # Devuelve el modo mirroring especificado en la ROM:
    # 0x00: horizontal
    # 0x01: vertical
    # 0x02: single
    # 0x03: 4-screen
    def get_mirroring(self):
        return self._mirroring


    # Devuelve el número de mapper
    def get_mapper_code(self):
        mapper_code = self._rom_control_1 >> 4
        mapper_code = mapper_code | (self._rom_control_2 & 0xF0)

        return mapper_code


    def get_control_1_mirroring_bit_0(self):
        return self._rom_control_1 & 0x01


    def get_control_1_trainer_bit_2(self):
        return (self._rom_control_1 & 0x04) >> 2


    def get_control_1_mirroring_bit_3(self):
        return (self._rom_control_1 & 0x08) >> 3


    # Devuelve el número de bancos de 16KB de memoria de programa disponibles
    def get_prg_count(self):
        return self._prg_count


    # Devuelve el número de bancos de 8KB de memoria de patrones gráficos disponibles
    def get_chr_count(self):
        return self._chr_count


    # Devuelve el banco PGR especificado por n
    def get_prg(self, n):
        return self._prg_banks[n]


    # Devuelve un banco PRG con direccionamiento como si fuesen de 8k en vez de 16k
    def get_prg_8k(self, n):
        number = n >> 1
        part = n & 0x01

        if part == 0:
            bank = self._prg_banks[number][0:8192]
        else:
            bank = self._prg_banks[number][8192:16384]

        return bank


    # Devuelve el banco CHR especificado por n
    def get_chr(self, n):
        return self._chr_banks[n]


    def get_chr_4h(self, n):
        bank_number = n / 2

        # Si es par es la primera mitad del banco de 8k
        if n & 0x01 == 0:
            return self._chr_banks[bank_number][0x0000:0x1000]
        else:
            return self._chr_banks[bank_number][0x1000:0x2000]


    # Devuelve un banco CHR con direccionamiento como si fuesen de 1k en vez de 8k
    def get_chr_1k(self, n):
        number = n >> 3
        part = n & 0x07
        addr = part * 1024

        bank = self._chr_banks[number][addr:addr + 1024]

        return bank





