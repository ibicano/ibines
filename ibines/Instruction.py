# -*- coding: utf-8 -*-

class Instruction(object):

    def __init__(self):
        pass

    # Ejecuta la instrucción
    def execute(self, cpu):
        pass

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __OPCODE = None


class BEQ(Instruction):

    def __init__(self):
        super(BEQ, self).__init__()

    def execute(self, cpu):
        pass

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __OPCODE = 0xF0




