# -*- coding: utf-8 -*-

class Instruction(object):

    def __init__(self, operands, cpu):
        self._operands = operands
        self._cpu = cpu

    # Ejecuta la instrucción
    def execute(self):
        pass

    # Devuelve el opcode de la instrucción
    def get_opcode(self):
        return self._OPCODE

    # Devuelve el número de ciclos de reloj en los que se ejecuta la instrucción
    def get_cycles(self):
        return self._CYCLES

    ###########################################################################
    # Variables privadas
    ###########################################################################
    _operands = None
    _cpu = None
    _OPCODE = None
    _BYTES = None
    _CYCLES = None


###############################################################################
# ADC: Add memory to accumulator with carry
###############################################################################
class ADC(Instruction):

    def __init__(self, operands, cpu):
        super(ADC, self).__init__(operands, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        carry = self._cpu.get_reg_p_c_bit()

        rst = ac + op + carry

        # Establece el bit CARRY del registro P
        self._cpu.set_carry_bit(rst)

        # Establece el bit ZERO del registro P
        self._cpu.set_zero_bit(rst)

        # Establece el bit OVERFLOW del registro P
        self._cpu.set_overflow_bit(op, rst)

        # Establece el bit SIGN del registro P
        self._cpu.set_sign_bit(rst)

        self._cpu.set_reg_a(rst)


class ADC_inmediate(ADC):

    def __init__(self, operands, cpu):
        super(ADC_inmediate, self).__init__(operands, cpu)

    def execute(self):
        op = self._operands[0]
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x69
    _BYTES = 2
    _CYCLES = 2


class ADC_zero(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_zero, self).__init__(operands, cpu)

    def execute(self):
        op = self._cpu.get_mem().read_data(self._operands[0])
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x65
    _BYTES = 2
    _CYCLES = 3


class ADC_zerox(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_zerox, self).__init__(operands, cpu)

    def execute(self):
        reg_x = self.__cpu.get_mem().get_reg_x()
        op = self._cpu.get_mem().read_data(self._operands[0] + reg_x)
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x75
    _BYTES = 2
    _CYCLES = 4


class ADC_abs(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_abs, self).__init__(operands, cpu)

    def execute(self):
        op = self._cpu.get_mem().read_data(self._operands[0])
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x60
    _BYTES = 3
    _CYCLES = 4


class ADC_absx(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_absx, self).__init__(operands, cpu)

    def execute(self):
        reg_x = self.__cpu.get_mem().get_reg_x()
        op = self._cpu.get_mem().read_data(self._operands[0] + reg_x)
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x70
    _BYTES = 3
    _CYCLES = 4


class ADC_absy(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_absx, self).__init__(operands, cpu)

    def execute(self):
        reg_y = self.__cpu.get_mem().get_reg_y()
        op = self._cpu.get_mem().read_data(self._operands[0] + reg_y)
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x79
    _BYTES = 3
    _CYCLES = 4

class ADC_preindexi(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_absx, self).__init__(operands, cpu)

    def execute(self):
        reg_x = self.__cpu.get_mem().get_reg_x()

        # Calcula el índice de la dirección donde se almacena la dirección
        # final del operando
        index = self.__operands[0] + reg_x

        # Calcula la dirección final del operando
        op_addr = self.__cpu.get_mem().read_data(index)
        op_addr = op_addr + (self.__cpu.get_mem().read_data(index+1) << 2)

        # Lee el operando usando su dirección
        op = self._cpu.get_mem().read_data(op_addr)
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x61
    _BYTES = 2
    _CYCLES = 6


class ADC_postindexi(Instruction):

    def __init__(self, operands, cpu):
        super(ADC_absx, self).__init__(operands, cpu)

    def execute(self):
        reg_y = self.__cpu.get_mem().get_reg_y()

        # Calcula el índice de la dirección donde se almacena la dirección
        # base del operando a la que se sumará el desplazamiento Y
        base_addr = self.__cpu.get_mem().read_data(self.__operands[0])
        base_addr = base_addr + (self.__cpu.get_mem().read_data(self.__operands[0]+1)) << 2

        op_addr = base_addr + reg_y

        op = self._cpu.get_mem().read_data(op_addr)
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x71
    _BYTES = 2
    _CYCLES = 5


###############################################################################

class BCC(Instruction):

    def __init__(self, operands, cpu):
        super(BCC, self).__init__(operands, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_c_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x90
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BCS(Instruction):

    def __init__(self, operands, cpu):
        super(BCS, self).__init__(operands, cpu)

    def execute(self):
        if self._cpu.get_reg_p_c_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _operand = None
    _OPCODE = 0xB0
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BEQ(Instruction):

    def __init__(self, operands, cpu):
        super(BEQ, self).__init__(operands, cpu)

    def execute(self):
        if self._cpu.get_reg_p_z_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0xF0
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BMI(Instruction):

    def __init__(self, operands, cpu):
        super(BMI, self).__init__(operands, cpu)

    def execute(self):
        if self._cpu.get_reg_p_n_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x30
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BNE(Instruction):

    def __init__(self, operands, cpu):
        super(BNE, self).__init__(operands, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_z_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0xD0
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BPL(Instruction):

    def __init__(self, operands, cpu):
        super(BPL, self).__init__(operands, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_n_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x10
    _BYTES = 2
    _CYCLES = 2