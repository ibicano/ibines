# -*- coding: utf-8 -*-


import time
import traceback
from ROM import ROM
from Mapper import Mapper
from PPU import *
from CPU import *
from Memory import Memory
from Instruction import *
from Input import Joypad
import os
import cProfile
import pstats


###############################################################################
# Clase: NES
# Descripción: Clase que implementa el sistema completo
###############################################################################
class NES(object):

    DEBUG = True

    def __init__(self, file_name):
        self._rom = ROM(file_name)
        self._mapper = Mapper.instance_mapper(self._rom.get_mapper_code(), self._rom)
        self._ppu = PPU(self._mapper)
        self._joypad_1 = Joypad()
        self._memory = Memory(self._ppu, self._mapper, self._joypad_1)
        self._cpu = CPU(self._memory, self._ppu)

        # Registros I/O del  JoyPad
        self._reg_joypad_1 = 0x00       # Dirección 0x4016 - read/write
        self._reg_joypad_2 = 0x00       # Dirección 0x4017 - read/write

    ###############################################################################
    # Función: run()
    # Descripción: Aquí se implementa el bucle principal de la NES. Cada iteración
    # ejecuta una instrucción llevando la cuenta de los ciclos de CPU consumidos
    # para sincronizarse con la PPU
    ###############################################################################
    def run(self):
        stats_cycles = 0                    # Ciclos de CPU ejecutados para fines estadisticos
        stats_total_time = time.time()      # Tiempo de ejecución transcurrido para fines estadísticos
        total_cycles = 0                    # Ciclos totales de CPU desde que se inicia el emulador
        key_counter = 0                     # Contador de ciclos hasta la siguiente comprobación de una pulsación de tecla
        cycles = 0                          # Ciclos de CPU de una iteración del bucle

        # Bucle principal
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

            # Aquí se detectan las pulsaciones en los dispositivos de entrada. Por cuestiones de rendimiento, ya que
            # es bastante caro comprobar en cada iteración del bucle, se hace solo cada 10000 ciclos de CPU
            key_counter += cycles
            if key_counter > 10000:
                # Eventos SDL (entrada por ejemplo)
                sdl_events = sdl2.ext.get_events()
                for e in sdl_events:
                    if e.type == sdl2.SDL_KEYDOWN:
                        if e.key.keysym.sym == sdl2.SDLK_w:
                            self._joypad_1.set_up(1)
                        elif e.key.keysym.sym == sdl2.SDLK_s:
                            self._joypad_1.set_down(1)
                        elif e.key.keysym.sym == sdl2.SDLK_a:
                            self._joypad_1.set_left(1)
                        elif e.key.keysym.sym == sdl2.SDLK_d:
                            self._joypad_1.set_right(1)
                        elif e.key.keysym.sym == sdl2.SDLK_o:
                            self._joypad_1.set_b(1)
                        elif e.key.keysym.sym == sdl2.SDLK_p:
                            self._joypad_1.set_a(1)
                        elif e.key.keysym.sym == sdl2.SDLK_RETURN:
                            self._joypad_1.set_start(1)
                        elif e.key.keysym.sym == sdl2.SDLK_RSHIFT:
                            self._joypad_1.set_select(1)
                    elif e.type == sdl2.SDL_KEYUP:
                        if e.key.keysym.sym == sdl2.SDLK_w:
                            self._joypad_1.set_up(0)
                        elif e.key.keysym.sym == sdl2.SDLK_s:
                            self._joypad_1.set_down(0)
                        elif e.key.keysym.sym == sdl2.SDLK_a:
                            self._joypad_1.set_left(0)
                        elif e.key.keysym.sym == sdl2.SDLK_d:
                            self._joypad_1.set_right(0)
                        elif e.key.keysym.sym == sdl2.SDLK_o:
                            self._joypad_1.set_b(0)
                        elif e.key.keysym.sym == sdl2.SDLK_p:
                            self._joypad_1.set_a(0)
                        elif e.key.keysym.sym == sdl2.SDLK_RETURN:
                            self._joypad_1.set_start(0)
                        elif e.key.keysym.sym == sdl2.SDLK_RSHIFT:
                            self._joypad_1.set_select(0)

                key_counter = 0

            total_cycles += cycles              # Incrementamos el contador de ciclos totales

            # Estadísticas
            stats_cycles += cycles

            # Hacemos la media de ciclos ejecutados por segundo para fines estadísticos
            if stats_cycles > 20000:
                stats_clock = time.time()

                if stats_clock - stats_total_time >= 1:
                    print str(stats_cycles) + " ciclos por segundo"
                    stats_cycles = 0
                    stats_total_time = stats_clock


            # Emula la velocidad de la NES
            #time.sleep(0.0000006)

            cycles = 0
            

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

nes.run()               # Ejecutamos

# Código de profiling
#cProfile.run("nes.run()", "profiling.log")
