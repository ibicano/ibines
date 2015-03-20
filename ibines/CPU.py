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
    def getRegPc(self):
        return self.__rereg_pc

    def getRegSp(self):
        return self.__rereg_sp

    def getRegA(self):
        return self.__rereg_a

    def getRegX(self):
        return self.__rereg_x

    def getRegY(self):
        return self.__rereg_y

    def getRegP(self):
        return self.__rereg_p

    # Escribe el contenido de los registros
    def setRegPc(self, r):
        self.__rereg_pc = r

    def setRegSp(self, r):
        self.__rereg_sp = r

    def setRegA(self, r):
        self.__rereg_a = r

    def setRegX(self, r):
        self.__rereg_x = r

    def setRegY(self, r):
        self.__rereg_y = r

    def setRegP(self, r):
        self.__rereg_p = r


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