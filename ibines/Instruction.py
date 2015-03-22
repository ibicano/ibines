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
    __BYTES = None
    __CYCLES = None


class BCC(Instruction, operand):

    def __init__(self):
        super(BEQ, self).__init__()
        self.__operand = operand

    def execute(self, cpu):
        if not cpu.get_reg_p_c_bit():
            cpu.set_reg_pc(cpu.get_reg_pc + self.operand)

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operand = None
    __OPCODE = 0x90
    __BYTES = 2
    __CYCLES = 2


class BCS(Instruction, operand):

    def __init__(self):
        super(BEQ, self).__init__()
        self.__operand = operand

    def execute(self, cpu):
        if cpu.get_reg_p_c_bit():
            cpu.set_reg_pc(cpu.get_reg_pc + self.operand)

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operand = None
    __OPCODE = 0xB0
    __BYTES = 2
    __CYCLES = 2


class BEQ(Instruction, operand):

    def __init__(self):
        super(BEQ, self).__init__()
        self.__operand = operand

    def execute(self, cpu):
        if cpu.get_reg_p_z_bit():
            cpu.set_reg_pc(cpu.get_reg_pc + self.operand)

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operand = None
    __OPCODE = 0xF0
    __BYTES = 2
    __CYCLES = 2


class BMI(Instruction, operand):

    def __init__(self):
        super(BEQ, self).__init__()
        self.__operand = operand

    def execute(self, cpu):
        if cpu.get_reg_p_n_bit():
            cpu.set_reg_pc(cpu.get_reg_pc + self.operand)

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operand = None
    __OPCODE = 0x30
    __BYTES = 2
    __CYCLES = 2


class BNE(Instruction, operand):

    def __init__(self):
        super(BEQ, self).__init__()
        self.__operand = operand

    def execute(self, cpu):
        if not cpu.get_reg_p_z_bit():
            cpu.set_reg_pc(cpu.get_reg_pc + self.operand)

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operand = None
    __OPCODE = 0xD0
    __BYTES = 2
    __CYCLES = 2


class BPL(Instruction, operand):

    def __init__(self):
        super(BEQ, self).__init__()
        self.__operand = operand

    def execute(self, cpu):
        if not cpu.get_reg_p_n_bit():
            cpu.set_reg_pc(cpu.get_reg_pc + self.operand)

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operand = None
    __OPCODE = 0x10
    __BYTES = 2
    __CYCLES = 2