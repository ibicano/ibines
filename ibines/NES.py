# -*- coding: utf-8 -*-


import time
from ROM import ROM
from PPU import *
from FastPPU import FastPPU
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
        #self._ppu = FastPPU(self._rom)

        self._ppu.set_mirroring(self._rom.get_mirroring())    # Establece el modo mirroring especificado en la ROM

        self._memory = Memory(self._ppu, self._rom)

        self._cpu = CPU(self._memory, self._ppu)
        #######################################################################
        #######################################################################


    # Aquí se implementa el bucle principal de la NES. Cada iteración equivale a un
    # ciclo de reloj, para más precisión y exactitud conceptual
    def run(self):
        #if NES.DEBUG: debug_file = open("/home/ibon/tmp/ibines.log", "w")

        stats_cycles = 0
        stats_total_time = 0
        #stats_counter = 0

        cycles = 0

        while 1:
            # Si hay interrupciones y la CPU no está ocupada, las lanzamos
            if self._ppu.get_int_vblank():
                self._cpu.interrupt_vblank()        # Procesamos VBLANK
                cycles += self._cpu.INT_LATENCY

            # Fetch y Exec siguiente instrucción (si hemos ejecutado una
            # interrupción en el paso anterior será su rutina de interrupción)
            #try:
            inst = self._cpu.fetch_inst()
                # if NES.DEBUG: debug_file.write(str(counter) + ": " + hex(self._cpu._reg_pc) + ": " + hex(inst.OPCODE) + str(inst.__class__) + "\n")
            cycles += inst.execute()
            #except OpcodeError as e:
                # if NES.DEBUG:
                #     debug_file.write(str(e) + "\n")
                #     debug_file.close()
            #    print "Error: Opcode inválido"
            #    print e

            # Restamos un ciclo de ejecución a la instrucción actual y la PPU

            self._ppu.exec_cycle(cycles)

            # Estadísticas
            #stats_counter += inst.CYCLES
            stats_cycles += cycles

            if stats_cycles % 5000 == 0:
                stats_clock = time.clock()

                if stats_clock - stats_total_time >= 1:
                    print str(stats_cycles) + " ciclos por segundo"
                    stats_cycles = 0
                    stats_total_time = stats_clock


            # Emula la velocidad de la NES
            #time.sleep(0.0000006)

            cycles = 0


###############################################################################
# Inicio del programa
###############################################################################
file_name = "../roms/Super Mario Bros. (E).nes"
nes = NES(file_name)
nes.run()