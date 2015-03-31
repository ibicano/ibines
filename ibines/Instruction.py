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


class ADC_zero(ADC):

    def __init__(self, operand, cpu):
        super(ADC_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(ADC_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0x65
    _BYTES = 2
    _CYCLES = 3


class ADC_zerox(ADC):

    def __init__(self, operand, cpu):
        super(ADC_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(ADC_zerox, self).execute(op)

    # Variables privadas
    _OPCODE = 0x75
    _BYTES = 2
    _CYCLES = 4


class ADC_abs(ADC):

    def __init__(self, operand, cpu):
        super(ADC_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(ADC_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0x60
    _BYTES = 3
    _CYCLES = 4


class ADC_absx(ADC):

    def __init__(self, operand, cpu):
        super(ADC_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(ADC_absx, self).execute(op)

    # Variables privadas
    _OPCODE = 0x70
    _BYTES = 3
    _CYCLES = 4


class ADC_absy(ADC):

    def __init__(self, operand, cpu):
        super(ADC_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        super(ADC_absy, self).execute(op)

    # Variables privadas
    _OPCODE = 0x79
    _BYTES = 3
    _CYCLES = 4

class ADC_preindexi(ADC):

    def __init__(self, operand, cpu):
        super(ADC_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        super(ADC_preindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x61
    _BYTES = 2
    _CYCLES = 6


class ADC_postindexi(ADC):

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

class AND_zero(AND):

    def __init__(self, operand, cpu):
        super(AND_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(AND_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0x25
    _BYTES = 2
    _CYCLES = 3


class AND_zerox(AND):

    def __init__(self, operand, cpu):
        super(AND_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(AND_zerox, self).execute(op)

    # Variables privadas
    _OPCODE = 0x35
    _BYTES = 2
    _CYCLES = 4


class AND_abs(AND):

    def __init__(self, operand, cpu):
        super(AND_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(AND_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0x2D
    _BYTES = 3
    _CYCLES = 4


class AND_absx(AND):

    def __init__(self, operand, cpu):
        super(AND_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(AND_absx, self).execute(op)

    # Variables privadas
    _OPCODE = 0x3D
    _BYTES = 3
    _CYCLES = 4


class AND_absy(AND):

    def __init__(self, operand, cpu):
        super(AND_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        super(AND_absy, self).execute(op)

    # Variables privadas
    _OPCODE = 0x39
    _BYTES = 3
    _CYCLES = 4

class AND_preindexi(AND):

    def __init__(self, operand, cpu):
        super(AND_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        super(AND_preindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x21
    _BYTES = 2
    _CYCLES = 6


class AND_postindexi(AND):

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
        op = self.fetch_accumulator_addrmode()
        result = super(ASL_accumulator, self).execute(op)
        self._cpu.set_reg_a(result)

    # Variables privadas
    _OPCODE = 0x0A
    _BYTES = 1
    _CYCLES = 2

class ASL_zero(ASL):

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


class ASL_zerox(ASL):

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


class ASL_abs(ASL):

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


class ASL_absx(ASL):

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


###############################################################################
# CLC Clear carry flag
###############################################################################
class CLC(Instruction):

    def __init__(self, cpu):
        super(CLC, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_c_bit(0)

    # Variables privadas
    _OPCODE = 0x18
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# CLD Clear decimal mode
###############################################################################
class CLD(Instruction):

    def __init__(self, cpu):
        super(CLD, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_d_bit(0)

    # Variables privadas
    _OPCODE = 0xD8
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# CLI Clear interrupt disable bit
###############################################################################
class CLI(Instruction):

    def __init__(self, cpu):
        super(CLI, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_i_bit(0)

    # Variables privadas
    _OPCODE = 0x58
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# CLV Clear overflow flag
###############################################################################
class CLV(Instruction):

    def __init__(self, cpu):
        super(CLV, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_v_bit(0)

    # Variables privadas
    _OPCODE = 0xB8
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# CMP Compare memory and accumulator
###############################################################################

class CMP(Instruction):

    def __init__(self, operand, cpu):
        super(CMP, self).__init__(operand, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        result = ac - op

        self._cpu.set_carry_bit(result)
        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)


class CMP_inmediate(CMP):

    def __init__(self, operand, cpu):
        super(CMP_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        super(CMP_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0xC9
    _BYTES = 2
    _CYCLES = 2

class CMP_zero(CMP):

    def __init__(self, operand, cpu):
        super(CMP_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(CMP_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0xC5
    _BYTES = 2
    _CYCLES = 3


class CMP_zerox(CMP):

    def __init__(self, operand, cpu):
        super(CMP_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(CMP_zerox, self).execute(op)

    # Variables privadas
    _OPCODE = 0xD5
    _BYTES = 2
    _CYCLES = 4


class CMP_abs(CMP):

    def __init__(self, operand, cpu):
        super(CMP_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(CMP_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0xCD
    _BYTES = 3
    _CYCLES = 4


class CMP_absx(CMP):

    def __init__(self, operand, cpu):
        super(CMP_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(CMP_absx, self).execute(op)

    # Variables privadas
    _OPCODE = 0xDD
    _BYTES = 3
    _CYCLES = 4


class CMP_absy(CMP):

    def __init__(self, operand, cpu):
        super(CMP_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        super(CMP_absy, self).execute(op)

    # Variables privadas
    _OPCODE = 0xD9
    _BYTES = 3
    _CYCLES = 4

class CMP_preindexi(CMP):

    def __init__(self, operand, cpu):
        super(CMP_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        super(CMP_preindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0xC1
    _BYTES = 2
    _CYCLES = 6


class CMP_postindexi(CMP):

    def __init__(self, operand, cpu):
        super(CMP_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        super(CMP_postindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0xD1
    _BYTES = 2
    _CYCLES = 5


###############################################################################
# CPX Compare Memory and Index X
###############################################################################

class CPX(Instruction):

    def __init__(self, operand, cpu):
        super(CPX, self).__init__(operand, cpu)

    def execute(self, op):
        reg_x = self._cpu.get_reg_x()
        result = reg_x - op

        self._cpu.set_carry_bit(result)
        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)


class CPX_inmediate(CPX):

    def __init__(self, operand, cpu):
        super(CPX_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        super(CPX_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0xE0
    _BYTES = 2
    _CYCLES = 2

class CPX_zero(CPX):

    def __init__(self, operand, cpu):
        super(CPX_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(CPX_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0xE4
    _BYTES = 2
    _CYCLES = 3


class CPX_abs(CPX):

    def __init__(self, operand, cpu):
        super(CPX_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(CPX_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0xEC
    _BYTES = 3
    _CYCLES = 4


###############################################################################
# CPY Compare Memory and Index Y
###############################################################################

class CPY(Instruction):

    def __init__(self, operand, cpu):
        super(CPY, self).__init__(operand, cpu)

    def execute(self, op):
        reg_y = self._cpu.get_reg_y()
        result = reg_y - op

        self._cpu.set_carry_bit(result)
        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)


class CPY_inmediate(CPY):

    def __init__(self, operand, cpu):
        super(CPY_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        super(CPY_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0xC0
    _BYTES = 2
    _CYCLES = 2

class CPY_zero(CPY):

    def __init__(self, operand, cpu):
        super(CPY_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(CPY_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0xC4
    _BYTES = 2
    _CYCLES = 3


class CPY_abs(CPY):

    def __init__(self, operand, cpu):
        super(CPY_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(CPY_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0xCC
    _BYTES = 3
    _CYCLES = 4


###############################################################################
# DEC Decrement memory by one
###############################################################################

class DEC(Instruction):

    def __init__(self, operand, cpu):
        super(DEC, self).__init__(operand, cpu)

    def execute(self, op):
        result = op - 1

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        return result


class DEC_zero(DEC):

    def __init__(self, operand, cpu):
        super(DEC_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(DEC_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xC6
    _BYTES = 2
    _CYCLES = 5


class DEC_zerox(DEC):

    def __init__(self, operand, cpu):
        super(DEC_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(DEC_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xD6
    _BYTES = 2
    _CYCLES = 6


class DEC_abs(DEC):

    def __init__(self, operand, cpu):
        super(DEC_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(DEC_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xCE
    _BYTES = 3
    _CYCLES = 6


class DEC_absx(DEC):

    def __init__(self, operand, cpu):
        super(DEC_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(DEC_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xDE
    _BYTES = 3
    _CYCLES = 7


###############################################################################
# DEX Decrement index X by one
###############################################################################

class DEX(Instruction):

    def __init__(self, cpu):
        super(DEX, self).__init__(None, cpu)

    def execute(self, op):
        result = self._cpu.get_reg_x() - 1

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_x(result)

    # Variables privadas
    _OPCODE = 0xCA
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# DEY Decrement index Y by one
###############################################################################

class DEY(Instruction):

    def __init__(self, cpu):
        super(DEY, self).__init__(None, cpu)

    def execute(self, op):
        result = self._cpu.get_reg_y() - 1

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_y(result)

    # Variables privadas
    _OPCODE = 0x88
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# EOR "Exclusive-Or" memory with accumulator
###############################################################################

class EOR(Instruction):

    def __init__(self, operand, cpu):
        super(EOR, self).__init__(operand, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        result = ac ^ op

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_a(result)


class EOR_inmediate(EOR):

    def __init__(self, operand, cpu):
        super(EOR_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        super(EOR_inmediate, self).execute(op)

    # Variables privadas
    _OPCODE = 0x49
    _BYTES = 2
    _CYCLES = 2

class EOR_zero(EOR):

    def __init__(self, operand, cpu):
        super(EOR_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(EOR_zero, self).execute(op)

    # Variables privadas
    _OPCODE = 0x45
    _BYTES = 2
    _CYCLES = 3


class EOR_zerox(EOR):

    def __init__(self, operand, cpu):
        super(EOR_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(EOR_zerox, self).execute(op)

    # Variables privadas
    _OPCODE = 0x55
    _BYTES = 2
    _CYCLES = 4


class EOR_abs(EOR):

    def __init__(self, operand, cpu):
        super(EOR_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        super(EOR_abs, self).execute(op)

    # Variables privadas
    _OPCODE = 0x40
    _BYTES = 3
    _CYCLES = 4


class EOR_absx(EOR):

    def __init__(self, operand, cpu):
        super(EOR_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        super(EOR_absx, self).execute(op)

    # Variables privadas
    _OPCODE = 0x50
    _BYTES = 3
    _CYCLES = 4


class EOR_absy(EOR):

    def __init__(self, operand, cpu):
        super(EOR_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        super(EOR_absy, self).execute(op)

    # Variables privadas
    _OPCODE = 0x59
    _BYTES = 3
    _CYCLES = 4

class EOR_preindexi(EOR):

    def __init__(self, operand, cpu):
        super(EOR_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        super(EOR_preindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x41
    _BYTES = 2
    _CYCLES = 6


class EOR_postindexi(EOR):

    def __init__(self, operand, cpu):
        super(EOR_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        super(EOR_postindexi, self).execute(op)

    # Variables privadas
    _OPCODE = 0x51
    _BYTES = 2
    _CYCLES = 5


###############################################################################
# INC Increment memory by one
###############################################################################

class INC(Instruction):

    def __init__(self, operand, cpu):
        super(INC, self).__init__(operand, cpu)

    def execute(self, op):
        result = op + 1

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        return result


class INC_zero(INC):

    def __init__(self, operand, cpu):
        super(INC_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(INC_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xE6
    _BYTES = 2
    _CYCLES = 5


class INC_zerox(INC):

    def __init__(self, operand, cpu):
        super(INC_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(INC_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xF6
    _BYTES = 2
    _CYCLES = 6


class INC_abs(INC):

    def __init__(self, operand, cpu):
        super(INC_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(INC_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xEE
    _BYTES = 3
    _CYCLES = 6


class INC_absx(INC):

    def __init__(self, operand, cpu):
        super(INC_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(INC_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

    # Variables privadas
    _OPCODE = 0xFE
    _BYTES = 3
    _CYCLES = 7


###############################################################################
# INX Increment Index X by one
###############################################################################

class INX(Instruction):

    def __init__(self, cpu):
        super(INX, self).__init__(None, cpu)

    def execute(self, op):
        result = self._cpu.get_reg_x() + 1

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_x(result)

    # Variables privadas
    _OPCODE = 0xE8
    _BYTES = 1
    _CYCLES = 2


###############################################################################
# INY Increment Index Y by one
###############################################################################

class INY(Instruction):

    def __init__(self, cpu):
        super(INY, self).__init__(None, cpu)

    def execute(self, op):
        result = self._cpu.get_reg_y() + 1

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_y(result)

    # Variables privadas
    _OPCODE = 0xC8
    _BYTES = 1
    _CYCLES = 2
