# -*- coding: utf-8 -*-


from ROM import ROM
from PPU import PPU
from CPU import CPU
from Memory import Memory
from Instruction import *



class NES(object):

    def __init__(self, file_name):
        #######################################################################
        # Variables de instancia
        #######################################################################
        file_name = "roms/Super Mario Bros. (E).nes"
        self._rom = ROM(file_name)
        self._ppu = PPU()
        self._memory = Memory(self._ppu, self._rom)
        self._cpu = CPU(memory, ppu)
        #######################################################################
        #######################################################################

    # Aquí se implementa el bucle principal. Cada iteración equivale a un
    # ciclo de reloj, para más precisión y exactitud conceptual
    def run(self):
        while True:
            # Si hay interrupciones y la CPU no está ocupada, las lanzamos

            # Si la CPU no está ocupada hacemos FETCH y EXEC

            # Restamos un ciclo de ejecución a la instrucción actual
            pass


###############################################################################
# Inicio del programa
###############################################################################
nes = NES()
nes.run()