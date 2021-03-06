# -*- coding: utf-8 -*-

import nesutils
import Instruction

"""
CPU

Descripción: Implementa la CPU del sistema
"""
class CPU(object):

    ###########################################################################
    # Constantes de clase
    ###########################################################################
    #Posiciones de los bits del registro de estado
    REG_P_BIT_C = 0
    REG_P_BIT_Z = 1
    REG_P_BIT_I = 2
    REG_P_BIT_D = 3
    REG_P_BIT_B = 4
    REG_P_BIT_V = 6
    REG_P_BIT_S = 7

    # Frecuencia de la CPU en Hz
    CPU_FREQ = 1660000

    # Direcciones de memoria vector de interrupciones
    INT_ADDR_VBLANK = 0xFFFA
    INT_ADDR_RESET = 0xFFFC
    INT_ADDR_IRQ = 0xFFFE

    # Latencia de interrupción en ciclos
    INT_LATENCY = 7

    ###########################################################################
    # Métodos públicos
    ###########################################################################

    # Constructor
    def __init__(self, mem, ppu):
        #######################################################################
        # Variables de instancia
        #######################################################################
        # Memoria del sistema
        self._mem = mem

        self._ppu = ppu

        # Registros
        # Program Counter (16-bit). Inicializa a la dirección de Reset
        self._reg_pc = self._mem.read_data(CPU.INT_ADDR_RESET)
        self._reg_pc = self._reg_pc | (self._mem.read_data(CPU.INT_ADDR_RESET + 1) << 8)

        self._reg_sp = 0xFF          # Stack Pointer (8-bit)
        self._reg_a = 0x00           # Accumulator (8-bit)
        self._reg_x = 0x00           # Index X (8-bit)
        self._reg_y = 0x00           # Index Y (8-bit)
        self._reg_p = 0x34           # Processor Status (8-bit)

        # Contadores de ciclos
        self._cycles_inst = 0

        # Indica si hay una IRQ pendiente
        self._irq = 0

        # Pool de instrucciones
        self._inst_pool = Instruction.InstructionPool(self)
        #######################################################################
        #######################################################################


    # Procesa una interrupción
    def interrupt(self, vector_addr):
        self.push_stack((self._reg_pc >> 8) & 0xFF)
        self.push_stack(self._reg_pc & 0xFF)
        # En las interrupciones el bit 4 se pone a 0 y el 5 a 1
        self.push_stack(self._reg_p & 0xEF | 0x20)
        self.set_reg_p_i_bit(1)
        addr = self._mem.read_data(vector_addr) & 0xFF
        addr = addr | (self._mem.read_data(vector_addr + 1) << 8)
        self._reg_pc = addr


    # procesa una interrupción IRQ
    def interrupt_irq(self):
        self._irq = 0
        self.interrupt(self.INT_ADDR_IRQ)


    # Procesa la interrupción VBlank
    def interrupt_vblank(self):
        self._ppu.set_int_vblank(0)
        self.interrupt(self.INT_ADDR_VBLANK)


    # Indica si hay una IRQ pendiente de ejecución
    def get_irq(self):
        return self._irq


    # Establece el valor del flag de activación de una IRQ
    def set_irq(self, v):
        self._irq = v


    # Devuelve una referencia a la memoria
    def get_mem(self):
        return self._mem


    # Devuelve el contenido los registros
    def get_reg_pc(self):
        return self._reg_pc

    def get_reg_sp(self):
        return self._reg_sp

    def get_reg_a(self):
        return self._reg_a

    def get_reg_x(self):
        return self._reg_x

    def get_reg_y(self):
        return self._reg_y

    def get_reg_p(self):
        return self._reg_p

    # Escribe el contenido de los registros
    def set_reg_pc(self, r):
        self._reg_pc = r & 0xFFFF

    def set_reg_sp(self, r):
        self._reg_sp = r & 0xFF

    def set_reg_a(self, r):
        self._reg_a = r & 0xFF

    def set_reg_x(self, r):
        self._reg_x = r & 0xFF

    def set_reg_y(self, r):
        self._reg_y = r & 0xFF

    def set_reg_p(self, r):
        self._reg_p = r & 0xFF

    # Incrementa el registro PC
    def incr_pc(self, n):
        self._reg_pc = (self._reg_pc + n) & 0xFFFF


    # Devuelve la instrucción a ejecutar
    def fetch_inst(self):
        opcode = self._mem.read_data(self._reg_pc)

        # Los comentarios de a continuación son por rendimiento
        inst = self._inst_pool.pool[opcode]

        if inst.BYTES == 2:                  # Instrucciones con operando de 1 byte
            operand = self._mem.read_data(self._reg_pc + 1)
            inst.set_operand(operand)
        elif inst.BYTES == 3:                  # Instrucciones con operando de 2 bytes
            operand = self._mem.read_data(self._reg_pc + 1)
            operand = operand | (self._mem.read_data(self._reg_pc + 2) << 8)
            inst.set_operand(operand)

        return inst


    # Devuelve el valor de los bits del registro de estado
    def get_reg_p_c_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_C)

    def get_reg_p_z_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_Z)

    def get_reg_p_i_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_I)

    def get_reg_p_d_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_D)

    def get_reg_p_b_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_B)

    def get_reg_p_v_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_V)

    def get_reg_p_s_bit(self):
        return nesutils.get_bit(self._reg_p, self.REG_P_BIT_S)

    # Establece el valor de los bits del registro de estado
    def set_reg_p_c_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_C, v)

    def set_reg_p_z_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_Z, v)

    def set_reg_p_i_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_I, v)

    def set_reg_p_d_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_D, v)

    def set_reg_p_b_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_B, v)

    def set_reg_p_v_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_V, v)

    def set_reg_p_s_bit(self, v):
        self._reg_p = nesutils.set_bit(self._reg_p, self.REG_P_BIT_S, v)

    # Establece el valor de los bits del registro de estado en función
    # del resultado de una instrucción
    def set_carry_bit(self, inst_result):
        if 0 <= inst_result < 0x100:
            self.set_reg_p_c_bit(0)
            return 0
        else:
            self.set_reg_p_c_bit(1)
            return 1


    def set_zero_bit(self, inst_result):
        rst = inst_result & 0xFF
        if rst == 0x00:
            self.set_reg_p_z_bit(1)
            return 1
        else:
            self.set_reg_p_z_bit(0)
            return 0

    def set_sign_bit(self, inst_result):
        rst = inst_result & 0xFF
        if rst & 0x80:
            self.set_reg_p_s_bit(1)
            return 1
        else:
            self.set_reg_p_s_bit(0)
            return 0

    # Funciones para meter y sacar datos de la Pila
    def push_stack(self, byte):
        sp_addr = 0x0100 | self.get_reg_sp()
        self.get_mem().write_data(byte, sp_addr)
        self.set_reg_sp(self.get_reg_sp() - 1)

    def pull_stack(self):
        sp_addr = 0x0100 | (self.get_reg_sp() + 1)
        byte = self.get_mem().read_data(sp_addr)
        self.set_reg_sp(self.get_reg_sp() + 1)
        return byte


# Excepciones

class OpcodeError(Exception):

    def __init__(self, addr, opcode):
        self._addr = addr
        self._opcode = opcode

    def __str__(self):
        return repr(hex(self._addr) + ": " + hex(self._opcode))
