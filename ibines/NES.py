# -*- coding: utf-8 -*-


import time
from ROM import ROM
from PPU import PPU
from CPU import *
from Memory import Memory
from Instruction import *



class NES(object):

    DEBUG = False

    def __init__(self, file_name):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._rom = ROM(file_name)

        self._ppu = PPU(self._rom)
        self._ppu.set_mirroring(self._rom.get_mirroring())    # Establece el modo mirroring especificado en la ROM

        self._memory = Memory(self._ppu, self._rom)

        self._cpu = CPU(self._memory, self._ppu)
        #######################################################################
        #######################################################################


    # Aquí se implementa el bucle principal de la NES. Cada iteración equivale a un
    # ciclo de reloj, para más precisión y exactitud conceptual
    def run(self):
        if NES.DEBUG: debug_file = open("/home/ibon/tmp/ibines.log", "w")

        cycles = 0
        total_time = 0
        counter = 0
        while True:
            loop_time = time.time()
            if not self._cpu.is_busy():
                # Si hay interrupciones y la CPU no está ocupada, las lanzamos
                if self._ppu.get_int_vblank():
                    self._cpu.interrupt_vblank()        # Procesamos VBLANK

                # Fetch y Exec siguiente instrucción (si hemos ejecutado una
                # interrupción en el paso anterior será su rutina de interrupción)
                try:
                    inst = self._cpu.fetch_inst()
                    if NES.DEBUG: debug_file.write(str(counter) + ": " + hex(self._cpu._reg_pc) + ": " + hex(inst.OPCODE) + str(inst.__class__) + "\n")
                    inst.execute()
                    counter += 1
                except OpcodeError as e:
                    if NES.DEBUG:
                        debug_file.write(str(e) + "\n")
                        debug_file.close()
                    print "Error: Opcode inválido"
                    print e


            # Restamos un ciclo de ejecución a la instrucción actual y la PPU
            self._cpu.exec_cycle()
            self._ppu.exec_cycle()

            cycles += 1

            if cycles % 1000 == 0:
                clock = time.clock()

                if clock - total_time >= 1:
                    print str(cycles / (clock - total_time)) + " ciclos por segundo"
                    cycles = 0
                    total_time = clock

            # Emula la velocidad de la NES
            #time.sleep(0.0000006)


###############################################################################
# Inicio del programa
###############################################################################
file_name = "../roms/Super Mario Bros. (E).nes"
nes = NES(file_name)
nes.run()