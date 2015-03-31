# -*- coding: utf-8 -*-

class Instruction(object):

    def __init__(self, operand, cpu):
        self._operand = operand
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

    # Calculan y devuelven el valor del operando y su posición de memoria
    # (cuando proceda) en forma de tupla (addr, data). Cuando el operando
    # operando no se ubica en una posición de memoria se devuelve sólo su valor
    def fetch_inmediate_addrmode(self):
        return self._operand

    def fetch_accumulator_addrmode(self):
        return self._cpu.get_reg_a()

    def fetch_absolute_addrmode(self):
        addr = self._operand
        data = self._cpu.get_mem().read_data(addr)
        return (addr, data)

    def fetch_indexed_x_addrmode(self):
        addr = self._operand + self._cpu.get_reg_x()
        data = self._cpu.get_mem().read_data(addr)
        return (addr, data)

    def fetch_indexed_y_addrmode(self):
        addr = self._operand + self._cpu.get_reg_y()
        data = self._cpu.get_mem().read_data(addr)
        return (addr, data)

    def fetch_preindexed_addrmode(self):
        # Calcula el índice de la dirección donde se almacena la dirección
        # final del operando
        index = self._operand + self._cpu.get_reg_x()

        # Calcula la dirección final del operando
        addr = self._cpu.get_mem().read_data(index)
        addr = addr + (self._cpu.get_mem().read_data(index+1) << 2)

        data = self._cpu.get_mem().read_data(addr)

        return (addr, data)

    def fetch_postindexed_addrmode(self):
        # Calcula el índice de la dirección donde se almacena la dirección
        # base del operando a la que se sumará el desplazamiento Y
        base_addr = self._cpu.get_mem().read_data(self._operand)
        base_addr = base_addr + (self._cpu.get_mem().read_data(self._operand+1)) << 2

        addr = base_addr + self._cpu.get_reg_y()

        data = self._cpu.get_mem().read_data(addr)

        return (addr, data)


    ###########################################################################
    # Variables privadas
    ###########################################################################
    _operand = None
    _cpu = None
    _OPCODE = None
    _BYTES = None
    _CYCLES = None


###############################################################################
# ADC: Add memory to accumulator with carry
###############################################################################
class ADC(Instruction):

    def __init__(self, operand, cpu):
        super(ADC, self).__init__(operand, cpu)

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

    def __init__(self, operand, cpu):
        super(ADC_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        super(ADC_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x69
    _BYTES = 2
    _CYCLES = 2


class ADC_zero(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(ADC_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0x65
    _BYTES = 2
    _CYCLES = 3


class ADC_zerox(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(ADC_zerox, self).execute(op)

    # Variables privadas
    _OPCODE = 0x75
    _BYTES = 2
    _CYCLES = 4


class ADC_abs(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(ADC_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0x60
    _BYTES = 3
    _CYCLES = 4


class ADC_absx(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(ADC_absx, self).execute(op)

    # Variables privadas
    _OPCODE = 0x70
    _BYTES = 3
    _CYCLES = 4


class ADC_absy(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        super(ADC_absy, self).execute(op)

    # Variables privadas
    _OPCODE = 0x79
    _BYTES = 3
    _CYCLES = 4

class ADC_preindexi(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        super(ADC_preindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x61
    _BYTES = 2
    _CYCLES = 6


class ADC_postindexi(Instruction):

    def __init__(self, operand, cpu):
        super(ADC_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        super(ADC_postindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x71
    _BYTES = 2
    _CYCLES = 5


###############################################################################
# AND: And memory with accumulator
###############################################################################

class AND(Instruction):

    def __init__(self, operand, cpu):
        super(AND, self).__init__(operand, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        result = ac & op

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_a(result)


class AND_inmediate(AND):

    def __init__(self, operand, cpu):
        super(AND_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        super(AND_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x29
    _BYTES = 2
    _CYCLES = 2

class AND_zero(Instruction):

    def __init__(self, operand, cpu):
        super(AND_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()
        super(AND_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0x25
    _BYTES = 2
    _CYCLES = 3


class AND_zerox(Instruction):

    def __init__(self, operand, cpu):
        super(AND_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(AND_zerox, self).execute(op)

    # Variables privadas
    _OPCODE = 0x35
    _BYTES = 2
    _CYCLES = 4


class AND_abs(Instruction):

    def __init__(self, operand, cpu):
        super(AND_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(AND_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0x2D
    _BYTES = 3
    _CYCLES = 4


class AND_absx(Instruction):

    def __init__(self, operand, cpu):
        super(AND_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(AND_absx, self).execute(op)

    # Variables privadas
    _OPCODE = 0x3D
    _BYTES = 3
    _CYCLES = 4


class AND_absy(Instruction):

    def __init__(self, operand, cpu):
        super(AND_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        super(AND_absy, self).execute(op)

    # Variables privadas
    _OPCODE = 0x39
    _BYTES = 3
    _CYCLES = 4

class AND_preindexi(Instruction):

    def __init__(self, operand, cpu):
        super(AND_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        super(AND_preindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x21
    _BYTES = 2
    _CYCLES = 6


class AND_postindexi(Instruction):

    def __init__(self, operand, cpu):
        super(AND_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        super(AND_postindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x31
    _BYTES = 2
    _CYCLES = 5


###############################################################################
# ASL: Shift Left One Bit (Memory or Accumulator)
###############################################################################

class ASL(Instruction):

    def __init__(self, operand, cpu):
        super(ASL, self).__init__(operand, cpu)

    def execute(self, op):
        result = op << 1

        self._cpu.set_carry_bit(result)
        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        return result


class ASL_accumulator(ASL):

    def __init__(self, operand, cpu):
        super(ASL_accumulator, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        result = super(ASL_accumulator, self).execute(op)
        self._cpu.set_reg_a(result)

    # Variables privadas
    _OPCODE = 0x0A
    _BYTES = 1
    _CYCLES = 2

class ASL_zero(Instruction):

    def __init__(self, operand, cpu):
        super(ASL_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()[1]
        result = super(ASL_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0x06
    _BYTES = 2
    _CYCLES = 5


class ASL_zerox(Instruction):

    def __init__(self, operand, cpu):
        super(ASL_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ASL_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0x16
    _BYTES = 2
    _CYCLES = 6


class ASL_abs(Instruction):

    def __init__(self, operand, cpu):
        super(ASL_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(ASL_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0x0E
    _BYTES = 3
    _CYCLES = 6


class ASL_absx(Instruction):

    def __init__(self, operand, cpu):
        super(ASL_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ASL_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0x1E
    _BYTES = 3
    _CYCLES = 7


###############################################################################

class BCC(Instruction):

    def __init__(self, operand, cpu):
        super(BCC, self).__init__(operand, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_c_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x90
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BCS(Instruction):

    def __init__(self, operand, cpu):
        super(BCS, self).__init__(operand, cpu)

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

    def __init__(self, operand, cpu):
        super(BEQ, self).__init__(operand, cpu)

    def execute(self):
        if self._cpu.get_reg_p_z_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0xF0
    _BYTES = 2
    _CYCLES = 2


###############################################################################
# BIT Test bits in memory with accumulator
###############################################################################
class BIT(Instruction):

    def __init__(self, operand, cpu):
        super(BIT, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]

        # Transfiere el bit de Signo
        if op & 0x80:
            self._cpu.set_reg_p_s_bit(1)
        else:
            self._cpu.set_reg_p_s_bit(1)

        # Transfiere el bit de Overflow
        if op & 0x40:
            self._cpu.set_reg_p_v_bit(1)
        else:
            self._cpu.set_reg_p_v_bit(1)

        # Calcula el bit Zero
        if not(op & self._cpu.get_reg_a()):
            self._cpu.set_reg_p_z_bit(1)
        else:
            self._cpu.set_reg_p_z_bit(0)


class BIT_zero(BIT):

    def __init__(self):
        super(BIT_zero, self).__init__()

    # Variables privadas
    _OPCODE = 0x24
    _BYTES = 2
    _CYCLES = 3


class BIT_abs(BIT):

    def __init__(self):
        super(BIT_abs, self).__init__()

    # Variables privadas
    _OPCODE = 0x2C
    _BYTES = 3
    _CYCLES = 4

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

    def __init__(self, operand, cpu):
        super(BNE, self).__init__(operand, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_z_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0xD0
    _BYTES = 2
    _CYCLES = 2

###############################################################################

class BPL(Instruction):

    def __init__(self, operand, cpu):
        super(BPL, self).__init__(operand, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_n_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x10
    _BYTES = 2
    _CYCLES = 2


###############################################################################
# BVC Branch on overflow clear
###############################################################################
class BVC(Instruction):

    def __init__(self, operand, cpu):
        super(BVC, self).__init__(operand, cpu)

    def execute(self):
        if not self._cpu.get_reg_p_v_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x50
    _BYTES = 2
    _CYCLES = 2


###############################################################################
# BVS Branch on overflow set
###############################################################################
class BVS(Instruction):

    def __init__(self, operand, cpu):
        super(BVS, self).__init__(operand, cpu)

    def execute(self):
        if self._cpu.get_reg_p_v_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc + self.operand)


    # Variables privadas
    _OPCODE = 0x70
    _BYTES = 2
    _CYCLES = 2

