# -*- coding: utf-8 -*-

class Instruction(object):

    def __init__(self, operands, cpu):
        seld.__operands = operands
        self.__cpu = cpu

    # Ejecuta la instrucción
    def execute(self):
        pass

    # Devuelve el opcode de la instrucción
    def get_opcode(self):
        return self.__OPCODE

    # Devuelve el número de ciclos de reloj en los que se ejecuta la instrucción
    def get_cycles(self):
        return self.__CYCLES

    ###########################################################################
    # Variables privadas
    ###########################################################################
    __operands = None
    __cpu = None
    __OPCODE = None
    __BYTES = None
    __CYCLES = None


###############################################################################
# ADC: Add memory to accumulator with carry
###############################################################################

class ADC_inmediate(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_inmediate, self).__init__(operands, cpu)

    def execute(self):
        ac = self.__cpu.get_reg_a()
        op = self.__operands[0]
        carry = self.__cpu.get_reg_p_c_bit()
        rst = ac + op + carry

        # Establece el bit CARRY del registro P
        if rst > 0x99:
            self.__cpu.set_reg_p_c_bit(1)
        else:
            self.__cpu.set_reg_p_c_bit(0)

        # Establece el bit ZERO del registro P
        if rst == 0x00:
            self.__cpu.set_reg_p_z_bit(1)
        else:
            self.__cpu.set_reg_p_z_bit(0)

        # Establece el bit OVERFLOW del registro P
        if ((not ((ac ^ op) & 0x80)) and ((ac ^ rst) & 0x80)):
            self.__cpu.set_reg_p_v(1)
        else:
            self.__cpu.set_reg_p_v(0)

        # Establece el bit SIGN del registro P
        if rst & 0x80:
            self.__cpu.set_reg_p_s_bit(1)
        else:
            self.__cpu.set_reg_p_s_bit(0)

        self.__cpu.set_reg_a(rst)

    # Variables privadas
    __OPCODE = 0x69
    __BYTES = 2
    __CYCLES = 2


# TODO: Completar instrucción
class ADC_zeropage(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_zeropage, self).__init__(operands, cpu)

    def execute(self):
        pass

    # Variables privadas
    __OPCODE = 0x65
    __BYTES = 2
    __CYCLES = 3







###############################################################################

class BCC(Instruction):

    def __init__(self, operands, cpu):
        super(BCC, self).__init__(operands, cpu)

    def execute(self):
        if not self.__cpu.get_reg_p_c_bit():
            self.__cpu.set_reg_pc(self.__cpu.get_reg_pc + self.operand)


    # Variables privadas
    __OPCODE = 0x90
    __BYTES = 2
    __CYCLES = 2

###############################################################################

class BCS(Instruction):

    def __init__(self, operands, cpu):
        super(BCS, self).__init__(operands, cpu)

    def execute(self):
        if self.__cpu.get_reg_p_c_bit():
            self.__cpu.set_reg_pc(self.__cpu.get_reg_pc + self.operand)


    # Variables privadas
    __operand = None
    __OPCODE = 0xB0
    __BYTES = 2
    __CYCLES = 2

###############################################################################

class BEQ(Instruction):

    def __init__(self, operands, cpu):
        super(BEQ, self).__init__(operands, cpu)

    def execute(self):
        if self.__cpu.get_reg_p_z_bit():
            self.__cpu.set_reg_pc(self.__cpu.get_reg_pc + self.operand)


    # Variables privadas
    __OPCODE = 0xF0
    __BYTES = 2
    __CYCLES = 2

###############################################################################

class BMI(Instruction):

    def __init__(self, operands, cpu):
        super(BMI, self).__init__(operands, cpu)

    def execute(self):
        if self.__cpu.get_reg_p_n_bit():
            self.__cpu.set_reg_pc(self.__cpu.get_reg_pc + self.operand)


    # Variables privadas
    __OPCODE = 0x30
    __BYTES = 2
    __CYCLES = 2

###############################################################################

class BNE(Instruction):

    def __init__(self, operands, cpu):
        super(BNE, self).__init__(operands, cpu)

    def execute(self):
        if not self.__cpu.get_reg_p_z_bit():
            self.__cpu.set_reg_pc(self.__cpu.get_reg_pc + self.operand)


    # Variables privadas
    __OPCODE = 0xD0
    __BYTES = 2
    __CYCLES = 2

###############################################################################

class BPL(Instruction):

    def __init__(self, operands, cpu):
        super(BPL, self).__init__(operands, cpu)

    def execute(self):
        if not self.__cpu.get_reg_p_n_bit():
            self.__cpu.set_reg_pc(self.__cpu.get_reg_pc + self.operand)


    # Variables privadas
    __OPCODE = 0x10
    __BYTES = 2
    __CYCLES = 2