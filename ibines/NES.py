# -*- coding: utf-8 -*-


import time
from ROM import ROM
from PPU import *
from FastPPU import FastPPU
from CPU import *
from Memory import Memory
from Instruction import *
import os



class NES(object):

    DEBUG = True

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
        if NES.DEBUG: debug_file = open("/home/ibon/tmp/ibines.log", "w")

        test = open("../tests/ibitest.log", "w")

        stats_cycles = 0
        stats_total_time = time.time()
        stats_counter = 0

        cycles = 0

        try:
            while 1:
                # Si hay interrupciones y la CPU no está ocupada, las lanzamos
                if self._ppu.get_int_vblank():
                    self._cpu.interrupt_vblank()        # Procesamos VBLANK
                    cycles += self._cpu.INT_LATENCY

                # Fetch y Exec siguiente instrucción (si hemos ejecutado una
                # interrupción en el paso anterior será su rutina de interrupción)
                try:
                    inst = self._cpu.fetch_inst()

                    # FIXME: código para depurar la salida de las instrucciones con nestest
                    test.write(self._log_inst(inst))

                    if NES.DEBUG: debug_file.write(str(stats_counter) + ": " + hex(self._cpu._reg_pc) + ": " + hex(inst.OPCODE) + str(inst.__class__) + "\n")
                    cycles += inst.execute()
                except OpcodeError as e:
                    if NES.DEBUG:
                        debug_file.close()
                    print "Error: Opcode inválido"
                    print e

                # Restamos un ciclo de ejecución a la instrucción actual y la PPU

                self._ppu.exec_cycle(cycles)

                # Estadísticas
                stats_counter += 1
                stats_cycles += cycles

                if stats_cycles > 5000:
                    stats_clock = time.time()

                    if stats_clock - stats_total_time >= 1:
                        print str(stats_cycles) + " ciclos por segundo"
                        stats_cycles = 0
                        stats_total_time = stats_clock


                # Emula la velocidad de la NES
                #time.sleep(0.0000006)

                cycles = 0
        except Exception as e:
            print "Cerrando fichero test"
            test.close()
            raise e

        test.close()


    def _log_inst(self, inst):
        s = str(hex(self._cpu._reg_pc))
        s += "  "
        op = inst.get_operand()

        if op != None:
            op_low = str(hex(op & 0xFF))
            op_high = str(hex((op >> 8) & 0xFF))
        else:
            op_low = ""
            op_high = ""

        s += str(hex(inst.OPCODE)) + "\t" + op_low + "\t" + op_high
        s += "\t\t\t" + "A:" + str(hex(self._cpu._reg_a))
        s += "\tX:" + str(hex(self._cpu._reg_x))
        s += "\tY:" + str(hex(self._cpu._reg_y))
        s += "\tP:" + str(hex(self._cpu._reg_p))
        s += "\tSP:" + str(hex(self._cpu._reg_sp)) + "\n"

        return s




###############################################################################
# Inicio del programa
###############################################################################

#file_name = "../roms/Super Mario Bros. (E).nes"
#file_name = "../roms/Donkey Kong Classics (USA, Europe).nes"
file_name = "../tests/nestest.nes"
nes = NES(file_name)
nes.run()