# -*- coding: utf-8 -*-

from Memory import Memory

class CPU(object):

    ###########################################################################
    # Métodos públicos
    ###########################################################################

    # Constructor
    def __init__(self, mem):
        self.mem = mem

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
        self.__reg_pc = r

    def set_reg_sp(self, r):
        self.__reg_sp = r

    def set_reg_a(self, r):
        self.__reg_a = r

    def set_reg_x(self, r):
        self.__reg_x = r

    def set_reg_y(self, r):
        self.__reg_y = r

    def set_reg_p(self, r):
        self.__reg_p = r


    # Devuelve el valor de los bits del registro de estado
    def get_reg_p_c_bit(self):
        return (0x01 & self.__reg_p)

    def get_reg_p_z_bit(self):
        return ((0x02 & self.__reg_p) >> 1)

    def get_reg_p_i_bit(self):
        return ((0x04 & self.__reg_p) >> 2)

    def get_reg_p_d_bit(self):
        return ((0x08 & self.__reg_p) >> 3)

    def get_reg_p_b_bit(self):
        return ((0x10 & self.__reg_p) >> 4)

    def get_reg_p_v_bit(self):
        return ((0x40 & self.__reg_p) >> 6)

    def get_reg_p_s_bit(self):
        return ((0x80 & self.__reg_p) >> 7)

    # Establece el valor de los bits del registro de estado
    def get_seg_p_c_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x01
        else:
            self.__reg_p = self.__reg_p & 0xFE

    def get_seg_p_z_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x02
        else:
            self.__reg_p = self.__reg_p & 0xFD

    def get_seg_p_i_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x04
        else:
            self.__reg_p = self.__reg_p & 0xFB

    def get_seg_p_d_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x08
        else:
            self.__reg_p = self.__reg_p & 0xF7

    def get_seg_p_b_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x10
        else:
            self.__reg_p = self.__reg_p & 0xEF

    def get_seg_p_v_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x40
        else:
            self.__reg_p = self.__reg_p & 0xBF

    def get_seg_p_s_bit(self, v):
        if v:
            self.__reg_p = self.__reg_p | 0x80
        else:
            self.__reg_p = self.__reg_p & 0x7F


    ###########################################################################
    # Variables privadas
    ###########################################################################

    # Registros
    __reg_pc = 0x0000        # Program Counter (16-bit)
    __reg_sp = 0x00          # Stack Pointer (8-bit)
    __reg_a = 0x00           # Accumulator (8-bit)
    __reg_x = 0x00           # Index X (8-bit)
    __reg_y = 0x00           # Index Y (8-bit)
    __reg_p = 0x00           # Processor Status (8-bit)

    # Referencia al sistema de memoria
    mem = None