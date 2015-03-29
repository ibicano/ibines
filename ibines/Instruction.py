# -*- coding: utf-8 -*-

class Instruction(object):

    def __init__(self, operands, cpu):
        self.__operands = operands
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
class ADC(Instruction):

    def __init__(self, operands, cpu):
        super(ADC, self).__init__(operands, cpu)

    def execute(self, op):
        ac = self.__cpu.get_reg_a()
        carry = self.__cpu.get_reg_p_c_bit()

        rst = ac + op + carry

        # Establece el bit CARRY del registro P
        self.__cpu.set_carry_bit(rst)

        # Establece el bit ZERO del registro P
        self.__cpu.set_zero_bit(rst)

        # Establece el bit OVERFLOW del registro P
        self.__cpu.set_overflow_bit(op, rst)

        # Establece el bit SIGN del registro P
        self.__cpu.set_sign_bit(rst)

        self.__cpu.set_reg_a(rst)


class ADC_inmediate(ADC):

    def __init__(self, operands, cpu):
        super(ADC_inmediate, self).__init__(operands, cpu)

    def execute(self):
        op = self.__operands[0]
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    __OPCODE = 0x69
    __BYTES = 2
    __CYCLES = 2


# TODO: Mirar lo del ambito de variables para ver si funciona bien la herencia
class ADC_absolute(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_absolute, self).__init__(operands, cpu)

    def execute(self):
        op = self.__cpu.get_mem().get_data(self.__operands[0])
        super(ADC_inmediate, self).execute(op)

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