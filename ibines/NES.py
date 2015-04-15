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
        self._ppu.set_mirroring(self._rom.get_mirroring())    # Establece el modo mirroring especificado en la ROM

        self._memory = Memory(self._ppu, self._rom)

        self._cpu = CPU(memory, ppu)
        #######################################################################
        #######################################################################

    # Aquí se implementa el bucle principal de la NES. Cada iteración equivale a un
    # ciclo de reloj, para más precisión y exactitud conceptual
    def run(self):
        while True:
            if not self._cpu.is_busy():
                # Si hay interrupciones y la CPU no está ocupada, las lanzamos
                if self._ppu.is_vblank():
                    self._cpu.interrupt_vblank()        # Procesamos VBLANK

                # Fetch y Exec siguiente instrucción (si hemos ejecutado una
                # interrupción en el paso anterior será su rutina de interrupción)
                inst = self._cpu.fetch()
                inst.execute()

            # Restamos un ciclo de ejecución a la instrucción actual y la PPU
            self._cpu.exec_cycle()
            self._ppu.exec_cycle()

            # Emula la velocidad de la NES
            time.sleep(0.0000006)


###############################################################################
# Inicio del programa
###############################################################################
nes = NES()
nes.run()