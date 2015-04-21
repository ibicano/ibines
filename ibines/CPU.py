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
        self._reg_pc = 0x8000        # Program Counter (16-bit)
        self._reg_sp = 0xFF          # Stack Pointer (8-bit)
        self._reg_a = 0x00           # Accumulator (8-bit)
        self._reg_x = 0x00           # Index X (8-bit)
        self._reg_y = 0x00           # Index Y (8-bit)
        self._reg_p = 0x00           # Processor Status (8-bit)

        # Contadores de ciclos
        self._cycles_inst = 0
        #######################################################################
        #######################################################################

    # Ejecuta un ciclo de reloj
    def exec_cycle(self):
        self._cycles_inst -= 1


    # Procesa una interrupción
    def interrupt(self, vector_addr):
        if not self.is_busy():
            self.push_stack((self._reg_pc >> 8) & 0xFF)
            self.push_stack(self._reg_pc & 0xFF)
            self.push_stack(self._reg_p)
            self.set_reg_p_i_bit(1)
            addr = self._mem.read_data(vector_addr) & 0xFF
            addr = addr | (self._mem.read_data(vector_addr + 1) << 8)
            self._reg_pc = addr

            return True
        else:
            return False


    # Procesa la interrupción VBlank
    def interrupt_vblank(self):
        self._ppu.set_int_vblank(0)
        return self.interrupt(self.INT_ADDR_VBLANK)


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

    # TODO: Aquí hay que leer la siguiente instrucción del PC, incrementar el PC
    # decodificarla a su objeto de clase "Instruction" correspondiente, poner los ciclos
    # de reloj de instrucción restantes a los de la instrucción decodificada
    # y delvolver el objeto
    # Devuelve la instrucción a ejecutar
    def fetch_inst(self):
        opcode = self._mem.read_data(self._reg_pc)

        if opcode in Instruction.Instruction.OPCODE_INDEX.keys():
            inst_class = Instruction.Instruction.OPCODE_INDEX[opcode]
        else:
            raise OpcodeError(self._reg_pc, opcode)

        inst = None

        if inst_class.BYTES == 1:                    # Instrucciones sin operando
            inst = inst_class(self)
        elif inst_class.BYTES == 2:                  # Instrucciones con operando de 1 byte
            operand = self._mem.read_data(self._reg_pc + 1)
            inst = inst_class(operand, self)
        elif inst_class.BYTES == 3:                  # Instrucciones con operando de 2 bytes
            operand = self._mem.read_data(self._reg_pc + 1)
            operand = operand | (self._mem.read_data(self._reg_pc + 2) << 8)
            inst = inst_class(operand, self)

        self._cycles_inst = inst.CYCLES

        return inst


    # Devuelve "True" si está en mitad de ejecución de una instrucción
    def is_busy(self):
        if self._cycles_inst > 0:
            return True
        else:
            return False

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
        if inst_result > 0xFF:
            self.set_reg_p_c_bit(1)
            return 1
        else:
            self.set_reg_p_c_bit(0)
            return 0

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

    def set_overflow_bit(self, src_op, inst_result):
        ac = self.get_reg_a()
        if ((not ((ac ^ src_op) & 0x80)) and ((ac ^ inst_result) & 0x80)):
            self.set_reg_p_v_bit(1)
            return 1
        else:
            self.set_reg_p_v_bit(0)
            return 0

    # Funciones para meter y sacar datos de la Pila
    def push_stack(self, byte):
        sp_addr = 0x0100 | self.get_reg_sp()
        self.get_mem().write_data(byte, sp_addr)
        self.set_reg_sp(self.get_reg_sp() - 1)

    def pull_stack(self):
        sp_addr = 0x0100 | self.get_reg_sp() + 1
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
