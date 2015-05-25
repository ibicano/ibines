# -*- coding: utf-8 -*-


import time
import traceback
from ROM import ROM
from Mapper import Mapper
from PPU import *
from CPU import *
from Memory import Memory
from Instruction import *
import os
import cProfile
import pstats



class NES(object):

    DEBUG = True

    def __init__(self, file_name):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._rom = ROM(file_name)
        self._mapper = Mapper.instance_mapper(self._rom.get_mapper_code(), self._rom)

        self._ppu = PPU(self._mapper)

        self._memory = Memory(self, self._ppu, self._mapper)

        self._cpu = CPU(self._memory, self._ppu)


        # Registros I/O del  JoyPad
        self._reg_joypad_1 = 0x00       # Dirección 0x4016 - read/write
        self._reg_joypad_2 = 0x00       # Dirección 0x4017 - read/write
        #######################################################################
        #######################################################################


    # Aquí se implementa el bucle principal de la NES. Cada iteración equivale a un
    # ciclo de reloj, para más precisión y exactitud conceptual
    def run(self):
        stats_cycles = 0
        stats_total_time = time.time()
        stats_counter = 0

        cycles = 0


        while 1:
            # Si hay interrupciones y la CPU no está ocupada, las lanzamos
            if self._ppu.get_int_vblank():
                self._cpu.interrupt_vblank()        # Procesamos VBLANK
                cycles += self._cpu.INT_LATENCY

            # Fetch y Exec siguiente instrucción (si hemos ejecutado una
            # interrupción en el paso anterior será su rutina de interrupción)
            inst = self._cpu.fetch_inst()
            cycles += inst.execute()

            # Restamos los ciclos de ejecución a la PPU
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



    def read_reg_4016(self):
        return self._reg_joypad_1


    def read_reg_4017(self):
        return self._reg_joypad_2


    def write_reg_4016(self, data):
        self._reg_joypad_1 = nesutils.set_bit(self._reg_joypad_1, 0, data & 0x01)


    def write_reg_4017(self, data):
        self._reg_joypad_2 = nesutils.set_bit(self._reg_joypad_2, 0, data & 0x01)


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

file_name = "../roms/Super Mario Bros. (E).nes"
#file_name = "../roms/Donkey Kong Classics (USA, Europe).nes"
#file_name = "../tests/nestest.nes"
#file_name = "../tests/instr_test-v4/rom_singles/10-branches.nes"
#file_name = "../tests/instr_test-v4/official_only.nes"
#file_name = "../tests/instr_test-v4/all_instrs.nes"
nes = NES(file_name)

nes.run()

# Código de profiling
#cProfile.run("nes.run()", "profiling.log")
