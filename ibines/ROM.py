# -*- coding: utf-8 -*-

# Clase que implementa la estructura de la ROM de un juego
# TODO: empollarse e implementar los mappers
class ROM(object):

    def __init__(self, file_name):
        self.load_file(file_name)

    def load_file(self, file_name):
        f = open(file_name, 'r')
        self._rom = list(bytearray(file.read()))
        f.close()

        # Comprueba que el formato de la cabecera sea corrector
        if (str(self._rom[0:3]) == "NES") and self._rom[3] == 0x1A:
            # Carga la cabecera
            self._pgr_rom_banks = self._rom[4]
            self._chr_rom_banks = self._rom[5]
            self._rom_control_1 = self._rom[6]
            self._rom_control_2 = self._rom[7]
            self._ram_banks = self._rom[8]
            self._reserved = self._rom[9]

            # Ahora carga la info
            i = 10
            # Si hay un trainer lo carga primero
            if self.get_control_1_trainer_bit_2():
                self._trainer = self._rom[i:i + 512]
                i += 512

            self._pgr_1 = self._rom[i:i + 16384]
            i += 16384

            # Si hay un segundo banco PGR lo carga
            if self._pgr_rom_banks == 2:
                self._pgr_2 = self._rom[i:i + 16384]
                i += 16384

            self._chr_1 = self._rom[i:i + 8192]
            i += 8192

            # Si hay un segundo banco CHR lo carga
            if self._chr_rom_banks == 2:
                self._chr_2 = self._rom[i:i + 8192]
                i += 8192

            self._load_ok = True
        else:
            self._load_ok = False
            print "Formato de fichero incorrecto"

    # Devuelve si la ROM ha cargado correctamente
    def get_load_ok(self):
        return self._load_ok

    def get_control_1_trainer_bit_2(self):
        return (self._rom_control_1 & 0x04) >> 2

    def get_pgr(self):
        return self._pgr_1 + self._pgr_2

    def read_pgr_data(self, addr):
        a = addr & 0xFFFF
        d = 0
        if a >= 0x0000 and a <= 0x3FFF:
            d = self._pgr_1[a]
        elif a >= 0x4000:
            d = self._pgr_2[a]

        return d


    ###########################################################################
    # Miembros privados
    ###########################################################################
    _rom = None            # Los bytes de la ROM en forma de lista

    _pgr_rom_banks = 0
    _chr_rom_banks = 0
    _rom_control_1 = 0x00
    _rom_control_2 = 0x00
    _ram_banks = 0
    _reserved = 0

    _pgr_1 = []
    _pgr_2 = []

    _chr_1 = []
    _chr_2 = []

    # Guarda si la ROM ha cargado correctamente
    _load_ok = False
