# -*- coding: utf-8 -*-

import nesutils

class CPU(object):

    ###########################################################################
    # Constantes
    ###########################################################################
    #Posiciones de los bits del registro de estado
    REG_P_BIT_C = 0
    REG_P_BIT_Z = 1
    REG_P_BIT_I = 2
    REG_P_BIT_D = 3
    REG_P_BIT_B = 4
    REG_P_BIT_V = 6
    REG_P_BIT_S = 7

    ###########################################################################
    # Métodos públicos
    ###########################################################################

    # Constructor
    def __init__(self, mem):
        self.__mem = mem

    # TODO: Terminar esta función
    # Bucle principal de ejecusión de la CPU
    def run(self):
        while True:
            self.incr_pc()
            inst = self.fetch_inst()
            inst.execute()

    # Devuelve una referencia a la memoria
    def get_mem(self):
        return self.__mem

    # Devuelve el contenido los registros
    def get_reg_pc(self):
        return self.__reg_pc

    def get_reg_sp(self):
        return self.__reg_sp

    def get_reg_a(self):
        return self.__reg_a

    def get_reg_x(self):
        return self.__reg_x

    def get_reg_y(self):
        return self.__reg_y

    def get_reg_p(self):
        return self.__reg_p

    # Escribe el contenido de los registros
    def set_reg_pc(self, r):
        self.__reg_pc = r & 0xFFFF

    def set_reg_sp(self, r):
        self.__reg_sp = r & 0xFF

    def set_reg_a(self, r):
        self.__reg_a = r & 0xFF

    def set_reg_x(self, r):
        self.__reg_x = r & 0xFF

    def set_reg_y(self, r):
        self.__reg_y = r & 0xFF

    def set_reg_p(self, r):
        self.__reg_p = r & 0xFF

    # Incrementa el registro PC
    def incr_pc(self):
        self.__reg_pc = (self.__reg_pc + 1) & 0xFFFF

    # Devuelve la instrucción actual
    def fetch_inst(self):
        pass

    # Devuelve el valor de los bits del registro de estado
    def get_reg_p_c_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_C)

    def get_reg_p_z_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_Z)

    def get_reg_p_i_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_I)

    def get_reg_p_d_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_D)

    def get_reg_p_b_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_B)

    def get_reg_p_v_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_V)

    def get_reg_p_s_bit(self):
        return nesutils.get_bit(self.__reg_p, self.REG_P_BIT_S)

    # Establece el valor de los bits del registro de estado
    def set_reg_p_c_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_C, v)

    def set_reg_p_z_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_Z, v)

    def set_reg_p_i_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_I, v)

    def set_reg_p_d_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_D, v)

    def set_reg_p_b_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_B, v)

    def set_reg_p_v_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_V, v)

    def set_reg_p_s_bit(self, v):
        nesutils.set_bit(self.__reg_p, self.REG_P_BIT_S, v)

    # Establece el valor de los bits del registro de estado en función
    # del resultado de una instrucción
    def set_carry_bit(self, inst_result):
        if inst_result > 0x99:
            self.set_reg_p_c_bit(1)
            return 1
        else:
            self.set_reg_p_c_bit(0)
            return 0

    def set_zero_bit(self, inst_result):
        if inst_result == 0x00:
            self.set_reg_p_z_bit(1)
            return 1
        else:
            self.set_reg_p_z_bit(0)
            return 0

    def set_sign_bit(self, inst_result):
        if inst_result & 0x80:
            self.set_reg_p_s_bit(1)
            return 1
        else:
            self.set_reg_p_s_bit(0)
            return 0

    def set_overflow_bit(self, src_op, inst_result):
        ac = self.get_reg_a()
        if ((not ((ac ^ src_op) & 0x80)) and ((ac ^ inst_result) & 0x80)):
            self.set_reg_p_v(1)
            return 1
        else:
            self.set_reg_p_v(0)
            return 0


    ###########################################################################
    # Variables protegidas
    ###########################################################################

    # Registros
    _reg_pc = 0x0000        # Program Counter (16-bit)
    _reg_sp = 0x00          # Stack Pointer (8-bit)
    _reg_a = 0x00           # Accumulator (8-bit)
    _reg_x = 0x00           # Index X (8-bit)
    _reg_y = 0x00           # Index Y (8-bit)
    _reg_p = 0x00           # Processor Status (8-bit)

    # Referencia al sistema de memoria
    _mem = None