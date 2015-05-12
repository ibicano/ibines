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

        self._pgr_count = 0
        self._chr_count = 0
        self._rom_control_1 = 0x00
        self._rom_control_2 = 0x00
        self._ram_count = 0
        self._reserved = [0x00] * 7

        self._pgr_1 = [0x00] * 0x4000
        self._pgr_2 = [0x00] * 0x4000

        self._chr_1 = [0x00] * 0x2000
        self._chr_2 = [0x00] * 0x2000

        # Guarda si la ROM ha cargado correctamente
        self._load_ok = False
        ###########################################################################
        ###########################################################################

        self.load_file(file_name)


    def load_file(self, file_name):
        f = open(file_name, 'r')
        self._rom = bytearray(f.read())
        f.close()

        # Comprueba que el formato de la cabecera sea corrector
        if (str(self._rom[0:3]) == "NES") and self._rom[3] == 0x1A:
            # Carga la cabecera
            self._pgr_count = self._rom[4]
            self._chr_count = self._rom[5]
            self._rom_control_1 = self._rom[6]
            self._rom_control_2 = self._rom[7]
            self._ram_count = self._rom[8]
            self._reserved = self._rom[9:16]

            # Reserva la memoria para almacenar los bancos en función del número de estos
            self._pgr_banks = [None] * self._pgr_count
            self._chr_banks = [None] * self._chr_count
            self._ram_banks = [None] * self._ram_count


            # Ahora carga la info. La variable i es el índice de lectura de la posición de la ROM
            i = 16      # Empezamos después de la cabecera

            # Si hay un trainer lo carga primero
            if self.get_control_1_trainer_bit_2():
                self._trainer = self._rom[i:i + 512]
                i += 512

            # Carga los bancos PGR
            for n in range(self._pgr_count):
                self._pgr_banks[n] = self._rom[i:i + 16384]
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
        if self.get_control_1_mirroring_bit_3() == 0:
            m = self.get_control_1_mirroring_bit_0()
        else:
            m = 0x03

        return m


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
    def get_pgr_count(self):
        return self._pgr_count


    # Devuelve el número de bancos de 16KB de memoria de patrones gráficos disponibles
    def get_chr_count(self):
        return self._chr_count


    # Devuelve el banco PGR especificado por n
    def get_pgr(self, n):
        return self._pgr_banks[n]


    # Devuelve el banco CHR especificado por n
    def get_chr(self, n):
        return self._chr_banks[n]


    def read_pgr_data(self, addr):
        a = addr & 0xFFFF
        d = 0x00
        if a < 0x4000:
            d = self._pgr_1[a]
        elif a >= 0x4000 and a < 0x8000:
            d = self._pgr_2[a % 0x4000]

        return d


    def read_chr_data(self, addr):
        a = addr & 0xFFFF
        d = 0x00
        if a < 0x1000:
            d = self._chr_1[a]
        elif a >= 0x1000 and a < 0x2000:
            d = self._chr_2[a % 0x1000]

        return d



