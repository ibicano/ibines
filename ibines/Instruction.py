# -*- coding: utf-8 -*-

import nesutils

"""
Instruction

Implementa la clase base para todas las instrucciones.
"""
class Instruction(object):

    def __init__(self, operand, cpu):
        #######################################################################
        # Variables de instancia
        #######################################################################
        self._operand = operand
        self._cpu = cpu


    # Ejecuta la instrucción e incrementa el registro PC de la CPU y devuelve el número de ciclos que ha tardado en ejecutar
    def execute(self):
        return self.CYCLES


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
        index = (self._operand + self._cpu.get_reg_x()) & 0xFF

        # Calcula la dirección final del operando
        addr = self._cpu.get_mem().read_data(index)
        addr = addr | (self._cpu.get_mem().read_data(index + 1) << 8)

        data = self._cpu.get_mem().read_data(addr)

        return (addr, data)


    def fetch_postindexed_addrmode(self):
        # Calcula el índice de la dirección donde se almacena la dirección
        # base del operando a la que se sumará el desplazamiento Y
        base_addr = self._cpu.get_mem().read_data(self._operand)
        base_addr = base_addr | (self._cpu.get_mem().read_data(self._operand + 1) << 8)

        addr = base_addr + self._cpu.get_reg_y()

        data = self._cpu.get_mem().read_data(addr)

        return (addr, data)


    # Devuelve el número de ciclos que tarda en ejecutarse la instrucción
    def get_cycles(self):
        return self.CYCLES


    ###########################################################################
    # Variables de clase
    ###########################################################################
    OPCODE = None
    BYTES = None
    CYCLES = None

    OPCODE_INDEX = None


###############################################################################
# ADC: Add memory to accumulator with carry
###############################################################################
class ADC(Instruction):

    def __init__(self, operand, cpu):
        super(ADC, self).__init__(operand, cpu)


    def execute(self, op):
        ac = self._cpu.get_reg_a()
        carry = self._cpu.get_reg_p_c_bit()

        tmp = op + carry
        rst = ac + tmp

        # Establece el bit CARRY del registro P
        self._cpu.set_carry_bit(rst)

        # Establece el bit ZERO del registro P
        self._cpu.set_zero_bit(rst)

        # Establece el bit OVERFLOW del registro P
        if ((not ((ac ^ tmp) & 0x80)) and ((ac ^ rst) & 0x80)):
            self._cpu.set_reg_p_v_bit(1)
        else:
            self._cpu.set_reg_p_v_bit(0)

        # Establece el bit SIGN del registro P
        self._cpu.set_sign_bit(rst)

        self._cpu.set_reg_a(rst)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class ADC_inmediate(ADC):

    def __init__(self, operand, cpu):
        super(ADC_inmediate, self).__init__(operand, cpu)


    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(ADC_inmediate, self).execute(op)


    # Variables privadas
    OPCODE = 0x69
    BYTES = 2
    CYCLES = 2


class ADC_zero(ADC):

    def __init__(self, operand, cpu):
        super(ADC_zero, self).__init__(operand, cpu)


    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(ADC_zero, self).execute(op)


    # Variables privadas
    OPCODE = 0x65
    BYTES = 2
    CYCLES = 3


class ADC_zerox(ADC):

    def __init__(self, operand, cpu):
        super(ADC_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(ADC_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0x75
    BYTES = 2
    CYCLES = 4


class ADC_abs(ADC):

    def __init__(self, operand, cpu):
        super(ADC_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(ADC_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0x6D
    BYTES = 3
    CYCLES = 4


class ADC_absx(ADC):

    def __init__(self, operand, cpu):
        super(ADC_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(ADC_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0x7D
    BYTES = 3
    CYCLES = 4


class ADC_absy(ADC):

    def __init__(self, operand, cpu):
        super(ADC_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(ADC_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0x79
    BYTES = 3
    CYCLES = 4

class ADC_preindexi(ADC):

    def __init__(self, operand, cpu):
        super(ADC_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(ADC_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x61
    BYTES = 2
    CYCLES = 6


class ADC_postindexi(ADC):

    def __init__(self, operand, cpu):
        super(ADC_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(ADC_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x71
    BYTES = 2
    CYCLES = 5


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

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class AND_inmediate(AND):

    def __init__(self, operand, cpu):
        super(AND_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(AND_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0x29
    BYTES = 2
    CYCLES = 2

class AND_zero(AND):

    def __init__(self, operand, cpu):
        super(AND_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(AND_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0x25
    BYTES = 2
    CYCLES = 3


class AND_zerox(AND):

    def __init__(self, operand, cpu):
        super(AND_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(AND_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0x35
    BYTES = 2
    CYCLES = 4


class AND_abs(AND):

    def __init__(self, operand, cpu):
        super(AND_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(AND_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0x2D
    BYTES = 3
    CYCLES = 4


class AND_absx(AND):

    def __init__(self, operand, cpu):
        super(AND_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(AND_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0x3D
    BYTES = 3
    CYCLES = 4


class AND_absy(AND):

    def __init__(self, operand, cpu):
        super(AND_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(AND_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0x39
    BYTES = 3
    CYCLES = 4

class AND_preindexi(AND):

    def __init__(self, operand, cpu):
        super(AND_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(AND_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x21
    BYTES = 2
    CYCLES = 6


class AND_postindexi(AND):

    def __init__(self, operand, cpu):
        super(AND_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(AND_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x31
    BYTES = 2
    CYCLES = 5


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

    def __init__(self, cpu):
        super(ASL_accumulator, self).__init__(None, cpu)

    def execute(self):
        op = self.fetch_accumulator_addrmode()
        result = super(ASL_accumulator, self).execute(op)
        self._cpu.set_reg_a(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES

    # Variables privadas
    OPCODE = 0x0A
    BYTES = 1
    CYCLES = 2

class ASL_zero(ASL):

    def __init__(self, operand, cpu):
        super(ASL_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()[1]
        result = super(ASL_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES

    # Variables privadas
    OPCODE = 0x06
    BYTES = 2
    CYCLES = 5


class ASL_zerox(ASL):

    def __init__(self, operand, cpu):
        super(ASL_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ASL_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES

    # Variables privadas
    OPCODE = 0x16
    BYTES = 2
    CYCLES = 6


class ASL_abs(ASL):

    def __init__(self, operand, cpu):
        super(ASL_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(ASL_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES

    # Variables privadas
    OPCODE = 0x0E
    BYTES = 3
    CYCLES = 6


class ASL_absx(ASL):

    def __init__(self, operand, cpu):
        super(ASL_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ASL_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES

    # Variables privadas
    OPCODE = 0x1E
    BYTES = 3
    CYCLES = 7


###############################################################################
# BCC Branch on Carry Clear
###############################################################################
class BCC(Instruction):

    def __init__(self, operand, cpu):
        super(BCC, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if not self._cpu.get_reg_p_c_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x90
    BYTES = 2
    CYCLES = 2

###############################################################################
# BCS Branch on carry set
###############################################################################
class BCS(Instruction):

    def __init__(self, operand, cpu):
        super(BCS, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if self._cpu.get_reg_p_c_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    _operand = None
    OPCODE = 0xB0
    BYTES = 2
    CYCLES = 2

###############################################################################
# BEQ Branch on result zero
###############################################################################
class BEQ(Instruction):

    def __init__(self, operand, cpu):
        super(BEQ, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if self._cpu.get_reg_p_z_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xF0
    BYTES = 2
    CYCLES = 2


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
            self._cpu.set_reg_p_s_bit(0)

        # Transfiere el bit de Overflow
        if op & 0x40:
            self._cpu.set_reg_p_v_bit(1)
        else:
            self._cpu.set_reg_p_v_bit(0)

        # Calcula el bit Zero
        if not(op & self._cpu.get_reg_a()):
            self._cpu.set_reg_p_z_bit(1)
        else:
            self._cpu.set_reg_p_z_bit(0)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class BIT_zero(BIT):

    def __init__(self, operand, cpu):
        return super(BIT_zero, self).__init__(operand, cpu)

    # Variables privadas
    OPCODE = 0x24
    BYTES = 2
    CYCLES = 3


class BIT_abs(BIT):

    def __init__(self, operand, cpu):
        return super(BIT_abs, self).__init__(operand, cpu)

    # Variables privadas
    OPCODE = 0x2C
    BYTES = 3
    CYCLES = 4


###############################################################################
# BMI Branch on result minus
###############################################################################
class BMI(Instruction):

    def __init__(self, operand, cpu):
        super(BMI, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if self._cpu.get_reg_p_s_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x30
    BYTES = 2
    CYCLES = 2


###############################################################################
# BNE Branch on result not zero
###############################################################################
class BNE(Instruction):

    def __init__(self, operand, cpu):
        super(BNE, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if not self._cpu.get_reg_p_z_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xD0
    BYTES = 2
    CYCLES = 2


###############################################################################
# BPL Branch on result plus
###############################################################################
class BPL(Instruction):

    def __init__(self, operand, cpu):
        super(BPL, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if not self._cpu.get_reg_p_s_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES

    # Variables privadas
    OPCODE = 0x10
    BYTES = 2
    CYCLES = 2


###############################################################################
# BRK Force Break
###############################################################################
class BRK(Instruction):

    def __init__(self, cpu):
        super(BRK, self).__init__(None, cpu)

    def execute(self):
        pc = self._cpu.get_reg_pc() + 1
        self._cpu.push_stack((pc >> 8) & 0xFF)
        self._cpu.push_stack(pc & 0xFF)
        self._cpu.set_reg_p_b_bit(1)
        self._cpu.push_stack(self._cpu.get_reg_p())
        self._cpu.set_reg_p_i_bit(1)

        pc = self._cpu.get_mem().read_data(0xFFFE)
        pc = pc | (self._cpu.get_mem().read_data(0xFFFF) << 8)
        self._cpu.set_reg_pc(pc)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x00
    BYTES = 1
    CYCLES = 2


###############################################################################
# BVC Branch on overflow clear
###############################################################################
class BVC(Instruction):

    def __init__(self, operand, cpu):
        super(BVC, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if not self._cpu.get_reg_p_v_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x50
    BYTES = 2
    CYCLES = 2


###############################################################################
# BVS Branch on overflow set
###############################################################################
class BVS(Instruction):

    def __init__(self, operand, cpu):
        super(BVS, self).__init__(operand, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if self._cpu.get_reg_p_v_bit():
            self._cpu.set_reg_pc(self._cpu.get_reg_pc() + nesutils.c2_to_int(self._operand))

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x70
    BYTES = 2
    CYCLES = 2


###############################################################################
# CLC Clear carry flag
###############################################################################
class CLC(Instruction):

    def __init__(self, cpu):
        super(CLC, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_c_bit(0)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x18
    BYTES = 1
    CYCLES = 2


###############################################################################
# CLD Clear decimal mode
###############################################################################
class CLD(Instruction):

    def __init__(self, cpu):
        super(CLD, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_d_bit(0)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xD8
    BYTES = 1
    CYCLES = 2


###############################################################################
# CLI Clear interrupt disable bit
###############################################################################
class CLI(Instruction):

    def __init__(self, cpu):
        super(CLI, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_i_bit(0)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x58
    BYTES = 1
    CYCLES = 2


###############################################################################
# CLV Clear overflow flag
###############################################################################
class CLV(Instruction):

    def __init__(self, cpu):
        super(CLV, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_v_bit(0)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xB8
    BYTES = 1
    CYCLES = 2


###############################################################################
# CMP Compare memory and accumulator
###############################################################################
class CMP(Instruction):

    def __init__(self, operand, cpu):
        super(CMP, self).__init__(operand, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        result = ac - op

        if 0 <= result < 0x100:
            self._cpu.set_reg_p_c_bit(1)
        else:
            self._cpu.set_reg_p_c_bit(0)

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class CMP_inmediate(CMP):

    def __init__(self, operand, cpu):
        super(CMP_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(CMP_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xC9
    BYTES = 2
    CYCLES = 2


class CMP_zero(CMP):

    def __init__(self, operand, cpu):
        super(CMP_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(CMP_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xC5
    BYTES = 2
    CYCLES = 3


class CMP_zerox(CMP):

    def __init__(self, operand, cpu):
        super(CMP_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(CMP_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0xD5
    BYTES = 2
    CYCLES = 4


class CMP_abs(CMP):

    def __init__(self, operand, cpu):
        super(CMP_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(CMP_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xCD
    BYTES = 3
    CYCLES = 4


class CMP_absx(CMP):

    def __init__(self, operand, cpu):
        super(CMP_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(CMP_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0xDD
    BYTES = 3
    CYCLES = 4


class CMP_absy(CMP):

    def __init__(self, operand, cpu):
        super(CMP_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(CMP_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0xD9
    BYTES = 3
    CYCLES = 4


class CMP_preindexi(CMP):

    def __init__(self, operand, cpu):
        super(CMP_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(CMP_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0xC1
    BYTES = 2
    CYCLES = 6


class CMP_postindexi(CMP):

    def __init__(self, operand, cpu):
        super(CMP_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(CMP_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0xD1
    BYTES = 2
    CYCLES = 5


###############################################################################
# CPX Compare Memory and Index X
###############################################################################
class CPX(Instruction):

    def __init__(self, operand, cpu):
        super(CPX, self).__init__(operand, cpu)

    def execute(self, op):
        reg_x = self._cpu.get_reg_x()
        result = reg_x - op

        if 0 <= result < 0x100:
            self._cpu.set_reg_p_c_bit(1)
        else:
            self._cpu.set_reg_p_c_bit(0)

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class CPX_inmediate(CPX):

    def __init__(self, operand, cpu):
        super(CPX_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(CPX_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xE0
    BYTES = 2
    CYCLES = 2


class CPX_zero(CPX):

    def __init__(self, operand, cpu):
        super(CPX_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(CPX_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xE4
    BYTES = 2
    CYCLES = 3


class CPX_abs(CPX):

    def __init__(self, operand, cpu):
        super(CPX_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(CPX_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xEC
    BYTES = 3
    CYCLES = 4


###############################################################################
# CPY Compare Memory and Index Y
###############################################################################
class CPY(Instruction):

    def __init__(self, operand, cpu):
        super(CPY, self).__init__(operand, cpu)

    def execute(self, op):
        reg_y = self._cpu.get_reg_y()
        result = reg_y - op

        if 0 <= result < 0x100:
            self._cpu.set_reg_p_c_bit(1)
        else:
            self._cpu.set_reg_p_c_bit(0)

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class CPY_inmediate(CPY):

    def __init__(self, operand, cpu):
        super(CPY_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(CPY_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xC0
    BYTES = 2
    CYCLES = 2


class CPY_zero(CPY):

    def __init__(self, operand, cpu):
        super(CPY_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(CPY_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xC4
    BYTES = 2
    CYCLES = 3


class CPY_abs(CPY):

    def __init__(self, operand, cpu):
        super(CPY_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(CPY_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xCC
    BYTES = 3
    CYCLES = 4


###############################################################################
# DEC Decrement memory by one
###############################################################################
class DEC(Instruction):

    def __init__(self, operand, cpu):
        super(DEC, self).__init__(operand, cpu)

    def execute(self, op):
        result = (op - 1) & 0xFF

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

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xC6
    BYTES = 2
    CYCLES = 5


class DEC_zerox(DEC):

    def __init__(self, operand, cpu):
        super(DEC_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(DEC_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xD6
    BYTES = 2
    CYCLES = 6


class DEC_abs(DEC):

    def __init__(self, operand, cpu):
        super(DEC_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(DEC_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xCE
    BYTES = 3
    CYCLES = 6


class DEC_absx(DEC):

    def __init__(self, operand, cpu):
        super(DEC_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(DEC_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xDE
    BYTES = 3
    CYCLES = 7


###############################################################################
# DEX Decrement index X by one
###############################################################################
class DEX(Instruction):

    def __init__(self, cpu):
        super(DEX, self).__init__(None, cpu)

    def execute(self):
        result = (self._cpu.get_reg_x() - 1) & 0xFF

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_x(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xCA
    BYTES = 1
    CYCLES = 2


###############################################################################
# DEY Decrement index Y by one
###############################################################################
class DEY(Instruction):

    def __init__(self, cpu):
        super(DEY, self).__init__(None, cpu)

    def execute(self):
        result = (self._cpu.get_reg_y() - 1) & 0xFF

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_y(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x88
    BYTES = 1
    CYCLES = 2


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

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class EOR_inmediate(EOR):

    def __init__(self, operand, cpu):
        super(EOR_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(EOR_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0x49
    BYTES = 2
    CYCLES = 2


class EOR_zero(EOR):

    def __init__(self, operand, cpu):
        super(EOR_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(EOR_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0x45
    BYTES = 2
    CYCLES = 3


class EOR_zerox(EOR):

    def __init__(self, operand, cpu):
        super(EOR_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(EOR_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0x55
    BYTES = 2
    CYCLES = 4


class EOR_abs(EOR):

    def __init__(self, operand, cpu):
        super(EOR_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(EOR_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0x4D
    BYTES = 3
    CYCLES = 4


class EOR_absx(EOR):

    def __init__(self, operand, cpu):
        super(EOR_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(EOR_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0x5D
    BYTES = 3
    CYCLES = 4


class EOR_absy(EOR):

    def __init__(self, operand, cpu):
        super(EOR_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(EOR_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0x59
    BYTES = 3
    CYCLES = 4


class EOR_preindexi(EOR):

    def __init__(self, operand, cpu):
        super(EOR_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(EOR_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x41
    BYTES = 2
    CYCLES = 6


class EOR_postindexi(EOR):

    def __init__(self, operand, cpu):
        super(EOR_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(EOR_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x51
    BYTES = 2
    CYCLES = 5


###############################################################################
# INC Increment memory by one
###############################################################################
class INC(Instruction):

    def __init__(self, operand, cpu):
        super(INC, self).__init__(operand, cpu)

    def execute(self, op):
        result = (op + 1) & 0xFF

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

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xE6
    BYTES = 2
    CYCLES = 5


class INC_zerox(INC):

    def __init__(self, operand, cpu):
        super(INC_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(INC_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xF6
    BYTES = 2
    CYCLES = 6


class INC_abs(INC):

    def __init__(self, operand, cpu):
        super(INC_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(INC_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xEE
    BYTES = 3
    CYCLES = 6


class INC_absx(INC):

    def __init__(self, operand, cpu):
        super(INC_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(INC_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xFE
    BYTES = 3
    CYCLES = 7


###############################################################################
# INX Increment Index X by one
###############################################################################
class INX(Instruction):

    def __init__(self, cpu):
        super(INX, self).__init__(None, cpu)

    def execute(self):
        result = (self._cpu.get_reg_x() + 1) & 0xFF

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_x(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xE8
    BYTES = 1
    CYCLES = 2


###############################################################################
# INY Increment Index Y by one
###############################################################################
class INY(Instruction):

    def __init__(self, cpu):
        super(INY, self).__init__(None, cpu)

    def execute(self):
        result = (self._cpu.get_reg_y() + 1) & 0xFF

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_y(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xC8
    BYTES = 1
    CYCLES = 2


###############################################################################
# JMP Jump to new location
###############################################################################
class JMP(Instruction):

    def __init__(self, operand, cpu):
        super(JMP, self).__init__(operand, cpu)

    def execute(self, op):
        self._cpu.set_reg_pc(op)
        return self.CYCLES


class JMP_abs(JMP):

    def __init__(self, operand, cpu):
        super(JMP_abs, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(JMP_abs, self).execute(addr)

    # Variables privadas
    OPCODE = 0x4C
    BYTES = 3
    CYCLES = 3


class JMP_indirect(JMP):

    def __init__(self, operand, cpu):
        super(JMP_indirect, self).__init__(operand, cpu)

    def execute(self):
        mem = self._cpu.get_mem()
        addr = mem.read_data(self._operand)
        addr = addr | (mem.read_data(self._operand + 1) << 8)

        return super(JMP_indirect, self).execute(addr)

    # Variables privadas
    OPCODE = 0x6C
    BYTES = 3
    CYCLES = 5


###############################################################################
# JSR Jump to new location saving return address
###############################################################################
class JSR(Instruction):

    def __init__(self, operand, cpu):
        super(JSR, self).__init__(operand, cpu)

    def execute(self):
        pc = self._cpu.get_reg_pc() + self.BYTES - 1
        self._cpu.push_stack((pc >> 8) & 0xFF)
        self._cpu.push_stack(pc & 0xFF)

        self._cpu.set_reg_pc(self._operand)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x20
    BYTES = 3
    CYCLES = 6


###############################################################################
# LDA Load accumulator with memory
###############################################################################
class LDA(Instruction):

    def __init__(self, operand, cpu):
        super(LDA, self).__init__(operand, cpu)

    def execute(self, op):
        # Establece el bit ZERO del registro P
        self._cpu.set_zero_bit(op)
        # Establece el bit SIGN del registro P
        self._cpu.set_sign_bit(op)

        self._cpu.set_reg_a(op)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class LDA_inmediate(LDA):

    def __init__(self, operand, cpu):
        super(LDA_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(LDA_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xA9
    BYTES = 2
    CYCLES = 2


class LDA_zero(LDA):

    def __init__(self, operand, cpu):
        super(LDA_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(LDA_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xA5
    BYTES = 2
    CYCLES = 3


class LDA_zerox(LDA):

    def __init__(self, operand, cpu):
        super(LDA_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(LDA_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0xB5
    BYTES = 2
    CYCLES = 4


class LDA_abs(LDA):

    def __init__(self, operand, cpu):
        super(LDA_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(LDA_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xAD
    BYTES = 3
    CYCLES = 4


class LDA_absx(LDA):

    def __init__(self, operand, cpu):
        super(LDA_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(LDA_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0xBD
    BYTES = 3
    CYCLES = 4


class LDA_absy(LDA):

    def __init__(self, operand, cpu):
        super(LDA_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(LDA_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0xB9
    BYTES = 3
    CYCLES = 4


class LDA_preindexi(LDA):

    def __init__(self, operand, cpu):
        super(LDA_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(LDA_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0xA1
    BYTES = 2
    CYCLES = 6


class LDA_postindexi(LDA):

    def __init__(self, operand, cpu):
        super(LDA_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(LDA_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0xB1
    BYTES = 2
    CYCLES = 5


###############################################################################
# LDX Load index X with memory
###############################################################################
class LDX(Instruction):

    def __init__(self, operand, cpu):
        super(LDX, self).__init__(operand, cpu)

    def execute(self, op):
        # Establece el bit ZERO del registro P
        self._cpu.set_zero_bit(op)
        # Establece el bit SIGN del registro P
        self._cpu.set_sign_bit(op)

        self._cpu.set_reg_x(op)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class LDX_inmediate(LDX):

    def __init__(self, operand, cpu):
        super(LDX_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(LDX_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xA2
    BYTES = 2
    CYCLES = 2


class LDX_zero(LDX):

    def __init__(self, operand, cpu):
        super(LDX_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(LDX_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xA6
    BYTES = 2
    CYCLES = 3


class LDX_zeroy(LDX):

    def __init__(self, operand, cpu):
        super(LDX_zeroy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(LDX_zeroy, self).execute(op)

    # Variables privadas
    OPCODE = 0xB6
    BYTES = 2
    CYCLES = 4


class LDX_abs(LDX):

    def __init__(self, operand, cpu):
        super(LDX_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(LDX_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xAE
    BYTES = 3
    CYCLES = 4


class LDX_absy(LDX):

    def __init__(self, operand, cpu):
        super(LDX_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(LDX_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0xBE
    BYTES = 3
    CYCLES = 4


###############################################################################
# LDY Load index Y with memory
###############################################################################
class LDY(Instruction):

    def __init__(self, operand, cpu):
        super(LDY, self).__init__(operand, cpu)

    def execute(self, op):
        # Establece el bit ZERO del registro P
        self._cpu.set_zero_bit(op)
        # Establece el bit SIGN del registro P
        self._cpu.set_sign_bit(op)

        self._cpu.set_reg_y(op)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class LDY_inmediate(LDY):

    def __init__(self, operand, cpu):
        super(LDY_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(LDY_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xA0
    BYTES = 2
    CYCLES = 2


class LDY_zero(LDY):

    def __init__(self, operand, cpu):
        super(LDY_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(LDY_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xA4
    BYTES = 2
    CYCLES = 3


class LDY_zerox(LDY):

    def __init__(self, operand, cpu):
        super(LDY_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(LDY_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0xB4
    BYTES = 2
    CYCLES = 4


class LDY_abs(LDY):

    def __init__(self, operand, cpu):
        super(LDY_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(LDY_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xAC
    BYTES = 3
    CYCLES = 4


class LDY_absx(LDY):

    def __init__(self, operand, cpu):
        super(LDY_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(LDY_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0xBC
    BYTES = 3
    CYCLES = 4


###############################################################################
# LSR Shift right one bit (memory or accumulator)
###############################################################################
class LSR(Instruction):

    def __init__(self, operand, cpu):
        super(LSR, self).__init__(operand, cpu)

    def execute(self, op):
        result = op >> 1

        self._cpu.set_reg_p_c_bit(op & 0x01)
        self._cpu.set_reg_p_s_bit(0)
        self._cpu.set_zero_bit(result)

        return result


class LSR_accumulator(LSR):

    def __init__(self, cpu):
        super(LSR_accumulator, self).__init__(None, cpu)

    def execute(self):
        op = self.fetch_accumulator_addrmode()
        result = super(LSR_accumulator, self).execute(op)
        self._cpu.set_reg_a(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x4A
    BYTES = 1
    CYCLES = 2


class LSR_zero(LSR):

    def __init__(self, operand, cpu):
        super(LSR_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(LSR_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x46
    BYTES = 2
    CYCLES = 5


class LSR_zerox(LSR):

    def __init__(self, operand, cpu):
        super(LSR_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(LSR_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x56
    BYTES = 2
    CYCLES = 6


class LSR_abs(LSR):

    def __init__(self, operand, cpu):
        super(LSR_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(LSR_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x4E
    BYTES = 3
    CYCLES = 6


class LSR_absx(LSR):

    def __init__(self, operand, cpu):
        super(LSR_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(LSR_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x5E
    BYTES = 3
    CYCLES = 7


###############################################################################
# NOP No operation
###############################################################################
class NOP(Instruction):

    def __init__(self, cpu):
        super(NOP, self).__init__(None, cpu)

    def execute(self):
        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xEA
    BYTES = 1
    CYCLES = 2


###############################################################################
# ORA "OR" memory with accumulator
###############################################################################
class ORA(Instruction):

    def __init__(self, operand, cpu):
        super(ORA, self).__init__(operand, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        result = ac | op

        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        self._cpu.set_reg_a(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class ORA_inmediate(ORA):

    def __init__(self, operand, cpu):
        super(ORA_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(ORA_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0x09
    BYTES = 2
    CYCLES = 2


class ORA_zero(ORA):

    def __init__(self, operand, cpu):
        super(ORA_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(ORA_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0x05
    BYTES = 2
    CYCLES = 3


class ORA_zerox(ORA):

    def __init__(self, operand, cpu):
        super(ORA_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(ORA_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0x15
    BYTES = 2
    CYCLES = 4


class ORA_abs(ORA):

    def __init__(self, operand, cpu):
        super(ORA_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(ORA_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0x0D
    BYTES = 3
    CYCLES = 4


class ORA_absx(ORA):

    def __init__(self, operand, cpu):
        super(ORA_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(ORA_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0x1D
    BYTES = 3
    CYCLES = 4


class ORA_absy(ORA):

    def __init__(self, operand, cpu):
        super(ORA_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(ORA_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0x19
    BYTES = 3
    CYCLES = 4


class ORA_preindexi(ORA):

    def __init__(self, operand, cpu):
        super(ORA_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(ORA_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x01
    BYTES = 2
    CYCLES = 6


class ORA_postindexi(ORA):

    def __init__(self, operand, cpu):
        super(ORA_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(ORA_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0x11
    BYTES = 2
    CYCLES = 5


###############################################################################
# PHA Push accumulator on stack
###############################################################################
class PHA(Instruction):

    def __init__(self, cpu):
        super(PHA, self).__init__(None, cpu)

    def execute(self):
        self._cpu.push_stack(self._cpu.get_reg_a())

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x48
    BYTES = 1
    CYCLES = 3


###############################################################################
# PHP Push processor status on stack
###############################################################################
class PHP(Instruction):

    def __init__(self, cpu):
        super(PHP, self).__init__(None, cpu)

    def execute(self):
        self._cpu.push_stack(self._cpu.get_reg_p())

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x08
    BYTES = 1
    CYCLES = 3


###############################################################################
# PLA Pull accumulator from stack
###############################################################################
class PLA(Instruction):

    def __init__(self, cpu):
        super(PLA, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_a(self._cpu.pull_stack())

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x68
    BYTES = 1
    CYCLES = 4


###############################################################################
# PLP Pull processor status from stack
###############################################################################
class PLP(Instruction):

    def __init__(self, cpu):
        super(PLP, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p(self._cpu.pull_stack())

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x28
    BYTES = 1
    CYCLES = 4


###############################################################################
# ROL Rotate one bit left (memory or accumulator)
###############################################################################
class ROL(Instruction):

    def __init__(self, operand, cpu):
        super(ROL, self).__init__(operand, cpu)

    def execute(self, op):
        result = op << 1
        if self._cpu.get_reg_p_c_bit():
            result = result | 0x01

        self._cpu.set_carry_bit(result)
        self._cpu.set_sign_bit(result)
        self._cpu.set_zero_bit(result)

        return result


class ROL_accumulator(ROL):

    def __init__(self, cpu):
        super(ROL_accumulator, self).__init__(None, cpu)

    def execute(self):
        op = self.fetch_accumulator_addrmode()
        result = super(ROL_accumulator, self).execute(op)
        self._cpu.set_reg_a(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x2A
    BYTES = 1
    CYCLES = 2


class ROL_zero(ROL):

    def __init__(self, operand, cpu):
        super(ROL_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(ROL_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x26
    BYTES = 2
    CYCLES = 5


class ROL_zerox(ROL):

    def __init__(self, operand, cpu):
        super(ROL_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ROL_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x36
    BYTES = 2
    CYCLES = 6


class ROL_abs(ROL):

    def __init__(self, operand, cpu):
        super(ROL_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(ROL_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x2E
    BYTES = 3
    CYCLES = 6


class ROL_absx(ROL):

    def __init__(self, operand, cpu):
        super(ROL_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ROL_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x3E
    BYTES = 3
    CYCLES = 7


###############################################################################
# ROR Rotate one bit right (memory or accumulator)
###############################################################################
class ROR(Instruction):

    def __init__(self, operand, cpu):
        super(ROR, self).__init__(operand, cpu)

    def execute(self, op):
        result = op >> 1

        if self._cpu.get_reg_p_c_bit():
            result = result | 0x80

        self._cpu.set_reg_p_c_bit(op & 0x01)
        self._cpu.set_reg_p_s_bit(result)
        self._cpu.set_zero_bit(result)

        return result


class ROR_accumulator(ROR):

    def __init__(self, cpu):
        super(ROR_accumulator, self).__init__(None, cpu)

    def execute(self):
        op = self.fetch_accumulator_addrmode()
        result = super(ROR_accumulator, self).execute(op)
        self._cpu.set_reg_a(result)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x6A
    BYTES = 1
    CYCLES = 2


class ROR_zero(ROR):

    def __init__(self, operand, cpu):
        super(ROR_zero, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(ROR_zero, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x66
    BYTES = 2
    CYCLES = 5


class ROR_zerox(ROR):

    def __init__(self, operand, cpu):
        super(ROR_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ROR_zerox, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x76
    BYTES = 2
    CYCLES = 6


class ROR_abs(ROR):

    def __init__(self, operand, cpu):
        super(ROR_abs, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_absolute_addrmode()
        result = super(ROR_abs, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x6E
    BYTES = 3
    CYCLES = 6


class ROR_absx(ROR):

    def __init__(self, operand, cpu):
        super(ROR_absx, self).__init__(operand, cpu)

    def execute(self):
        addr, op = self.fetch_indexed_x_addrmode()
        result = super(ROR_absx, self).execute(op)
        self._cpu.get_mem().write_data(result, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x7E
    BYTES = 3
    CYCLES = 7


###############################################################################
# RTI Return from interrupt
###############################################################################
class RTI(Instruction):

    def __init__(self, cpu):
        super(RTI, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p(self._cpu.pull_stack())

        pc = self._cpu.pull_stack()
        pc = pc | (self._cpu.pull_stack() << 8)
        self._cpu.set_reg_pc(pc)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x40
    BYTES = 1
    CYCLES = 6


###############################################################################
# RTS Return from subroutine
###############################################################################
class RTS(Instruction):

    def __init__(self, cpu):
        super(RTS, self).__init__(None, cpu)

    def execute(self):
        pc = self._cpu.pull_stack()
        pc = pc | (self._cpu.pull_stack() << 8)
        pc = pc + 1
        self._cpu.set_reg_pc(pc)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x60
    BYTES = 1
    CYCLES = 6


###############################################################################
# SBC Subtract memory from accumulator with borrow
###############################################################################
class SBC(Instruction):

    def __init__(self, operand, cpu):
        super(SBC, self).__init__(operand, cpu)

    def execute(self, op):
        ac = self._cpu.get_reg_a()
        carry = self._cpu.get_reg_p_c_bit()

        tmp = op - carry
        rst = ac - tmp

        # Establece el bit CARRY del registro P
        if 0 <= rst < 0x100:
            self._cpu.set_reg_p_c_bit(1)
        else:
            self._cpu.set_reg_p_c_bit(0)

        # Establece el bit ZERO del registro P
        self._cpu.set_zero_bit(rst)

        # Establece el bit OVERFLOW del registro P
        if (((ac ^ tmp) & 0x80) and ((ac ^ rst) & 0x80)):
            self._cpu.set_reg_p_v_bit(1)
        else:
            self._cpu.set_reg_p_v_bit(0)

        # Establece el bit SIGN del registro P
        self._cpu.set_sign_bit(rst)

        self._cpu.set_reg_a(rst)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


class SBC_inmediate(SBC):

    def __init__(self, operand, cpu):
        super(SBC_inmediate, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_inmediate_addrmode()
        return super(SBC_inmediate, self).execute(op)

    # Variables privadas
    OPCODE = 0xE9
    BYTES = 2
    CYCLES = 2


class SBC_zero(SBC):

    def __init__(self, operand, cpu):
        super(SBC_zero, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(SBC_zero, self).execute(op)

    # Variables privadas
    OPCODE = 0xE5
    BYTES = 2
    CYCLES = 3


class SBC_zerox(SBC):

    def __init__(self, operand, cpu):
        super(SBC_zerox, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(SBC_zerox, self).execute(op)

    # Variables privadas
    OPCODE = 0xF5
    BYTES = 2
    CYCLES = 4


class SBC_abs(SBC):

    def __init__(self, operand, cpu):
        super(SBC_abs, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_absolute_addrmode()[1]
        return super(SBC_abs, self).execute(op)

    # Variables privadas
    OPCODE = 0xED
    BYTES = 3
    CYCLES = 4


class SBC_absx(SBC):

    def __init__(self, operand, cpu):
        super(SBC_absx, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_x_addrmode()[1]
        return super(SBC_absx, self).execute(op)

    # Variables privadas
    OPCODE = 0xFD
    BYTES = 3
    CYCLES = 4


class SBC_absy(SBC):

    def __init__(self, operand, cpu):
        super(SBC_absy, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_indexed_y_addrmode()[1]
        return super(SBC_absy, self).execute(op)

    # Variables privadas
    OPCODE = 0xF9
    BYTES = 3
    CYCLES = 4


class SBC_preindexi(SBC):

    def __init__(self, operand, cpu):
        super(SBC_preindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_preindexed_addrmode()[1]
        return super(SBC_preindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0xE1
    BYTES = 2
    CYCLES = 6


class SBC_postindexi(SBC):

    def __init__(self, operand, cpu):
        super(SBC_postindexi, self).__init__(operand, cpu)

    def execute(self):
        op = self.fetch_postindexed_addrmode()[1]
        return super(SBC_postindexi, self).execute(op)

    # Variables privadas
    OPCODE = 0xF1
    BYTES = 2
    CYCLES = 5


###############################################################################
# SEC Set carry flag
###############################################################################
class SEC(Instruction):

    def __init__(self, cpu):
        super(SEC, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_c_bit(1)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x38
    BYTES = 1
    CYCLES = 2


###############################################################################
# SED Set decimal mode
###############################################################################
class SED(Instruction):

    def __init__(self, cpu):
        super(SED, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_d_bit(1)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xF8
    BYTES = 1
    CYCLES = 2


###############################################################################
# SEI Set interrupt disable status
###############################################################################
class SEI(Instruction):

    def __init__(self, cpu):
        super(SEI, self).__init__(None, cpu)

    def execute(self):
        self._cpu.set_reg_p_i_bit(1)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x78
    BYTES = 1
    CYCLES = 2


###############################################################################
# STA Store accumulator in memory
###############################################################################
class STA(Instruction):

    def __init__(self, operand, cpu):
        super(STA, self).__init__(operand, cpu)

    def execute(self, addr):
        ac = self._cpu.get_reg_a()
        self._cpu.get_mem().write_data(ac, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if addr != 0x4014:
            return self.CYCLES
        else:
            return self.CYCLES + 512


class STA_zero(STA):

    def __init__(self, operand, cpu):
        super(STA_zero, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(STA_zero, self).execute(addr)

    # Variables privadas
    OPCODE = 0x85
    BYTES = 2
    CYCLES = 3


class STA_zerox(STA):

    def __init__(self, operand, cpu):
        super(STA_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_indexed_x_addrmode()[0]
        return super(STA_zerox, self).execute(addr)

    # Variables privadas
    OPCODE = 0x95
    BYTES = 2
    CYCLES = 4


class STA_abs(STA):

    def __init__(self, operand, cpu):
        super(STA_abs, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(STA_abs, self).execute(addr)

    # Variables privadas
    OPCODE = 0x8D
    BYTES = 3
    CYCLES = 4


class STA_absx(STA):

    def __init__(self, operand, cpu):
        super(STA_absx, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_indexed_x_addrmode()[0]
        return super(STA_absx, self).execute(addr)

    # Variables privadas
    OPCODE = 0x9D
    BYTES = 3
    CYCLES = 5


class STA_absy(STA):

    def __init__(self, operand, cpu):
        super(STA_absy, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_indexed_y_addrmode()[0]
        return super(STA_absy, self).execute(addr)

    # Variables privadas
    OPCODE = 0x99
    BYTES = 3
    CYCLES = 5

class STA_preindexi(STA):

    def __init__(self, operand, cpu):
        super(STA_preindexi, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_preindexed_addrmode()[0]
        return super(STA_preindexi, self).execute(addr)

    # Variables privadas
    OPCODE = 0x81
    BYTES = 2
    CYCLES = 6


class STA_postindexi(STA):

    def __init__(self, operand, cpu):
        super(STA_postindexi, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_postindexed_addrmode()[0]
        return super(STA_postindexi, self).execute(addr)

    # Variables privadas
    OPCODE = 0x91
    BYTES = 2
    CYCLES = 6


###############################################################################
# STX Store index X in memory
###############################################################################
class STX(Instruction):

    def __init__(self, operand, cpu):
        super(STX, self).__init__(operand, cpu)

    def execute(self, addr):
        reg_x = self._cpu.get_reg_x()
        self._cpu.get_mem().write_data(reg_x, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if addr != 0x4014:
            return self.CYCLES
        else:
            return self.CYCLES + 512


class STX_zero(STX):

    def __init__(self, operand, cpu):
        super(STX_zero, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(STX_zero, self).execute(addr)

    # Variables privadas
    OPCODE = 0x86
    BYTES = 2
    CYCLES = 3


class STX_zeroy(STX):

    def __init__(self, operand, cpu):
        super(STX_zeroy, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_indexed_y_addrmode()[0]
        return super(STX_zeroy, self).execute(addr)

    # Variables privadas
    OPCODE = 0x96
    BYTES = 2
    CYCLES = 4


class STX_abs(STX):

    def __init__(self, operand, cpu):
        super(STX_abs, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(STX_abs, self).execute(addr)

    # Variables privadas
    OPCODE = 0x8E
    BYTES = 3
    CYCLES = 4


###############################################################################
# STY Store index Y in memory
###############################################################################
class STY(Instruction):

    def __init__(self, operand, cpu):
        super(STY, self).__init__(operand, cpu)

    def execute(self, addr):
        reg_y = self._cpu.get_reg_y()
        self._cpu.get_mem().write_data(reg_y, addr)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        if addr != 0x4014:
            return self.CYCLES
        else:
            return self.CYCLES + 512


class STY_zero(STY):

    def __init__(self, operand, cpu):
        super(STY_zero, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(STY_zero, self).execute(addr)

    # Variables privadas
    OPCODE = 0x84
    BYTES = 2
    CYCLES = 3


class STY_zerox(STY):

    def __init__(self, operand, cpu):
        super(STY_zerox, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_indexed_x_addrmode()[0]
        return super(STY_zerox, self).execute(addr)

    # Variables privadas
    OPCODE = 0x94
    BYTES = 2
    CYCLES = 4


class STY_abs(STY):

    def __init__(self, operand, cpu):
        super(STY_abs, self).__init__(operand, cpu)

    def execute(self):
        addr = self.fetch_absolute_addrmode()[0]
        return super(STY_abs, self).execute(addr)

    # Variables privadas
    OPCODE = 0x8C
    BYTES = 3
    CYCLES = 4


###############################################################################
# TAX Transfer accumulator to index X
###############################################################################
class TAX(Instruction):

    def __init__(self, cpu):
        super(TAX, self).__init__(None, cpu)

    def execute(self):
        ac = self._cpu.get_reg_a()

        self._cpu.set_carry_bit(ac)
        self._cpu.set_sign_bit(ac)

        self._cpu.set_reg_x(ac)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xAA
    BYTES = 1
    CYCLES = 2


###############################################################################
# TAY Transfer accumulator to index Y
###############################################################################
class TAY(Instruction):

    def __init__(self, cpu):
        super(TAY, self).__init__(None, cpu)

    def execute(self):
        ac = self._cpu.get_reg_a()

        self._cpu.set_carry_bit(ac)
        self._cpu.set_sign_bit(ac)

        self._cpu.set_reg_y(ac)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xA8
    BYTES = 1
    CYCLES = 2


###############################################################################
# TSX Transfer stack pointer to index X
###############################################################################
class TSX(Instruction):

    def __init__(self, cpu):
        super(TSX, self).__init__(None, cpu)

    def execute(self):
        sp = self._cpu.get_reg_sp()

        self._cpu.set_carry_bit(sp)
        self._cpu.set_sign_bit(sp)

        self._cpu.set_reg_x(sp)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0xBA
    BYTES = 1
    CYCLES = 2


###############################################################################
# TXA Transfer index X to accumulator
###############################################################################
class TXA(Instruction):

    def __init__(self, cpu):
        super(TXA, self).__init__(None, cpu)

    def execute(self):
        reg_x = self._cpu.get_reg_x()

        self._cpu.set_carry_bit(reg_x)
        self._cpu.set_sign_bit(reg_x)

        self._cpu.set_reg_a(reg_x)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x8A
    BYTES = 1
    CYCLES = 2


###############################################################################
# TXS Transfer index X to stack pointer
###############################################################################
class TXS(Instruction):

    def __init__(self, cpu):
        super(TXS, self).__init__(None, cpu)

    def execute(self):
        reg_x = self._cpu.get_reg_x()

        self._cpu.set_reg_sp(reg_x)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x9A
    BYTES = 1
    CYCLES = 2


###############################################################################
# TYA Transfer index Y to accumulator
###############################################################################
class TYA(Instruction):

    def __init__(self, cpu):
        super(TYA, self).__init__(None, cpu)

    def execute(self):
        reg_y = self._cpu.get_reg_y()

        self._cpu.set_carry_bit(reg_y)
        self._cpu.set_sign_bit(reg_y)

        self._cpu.set_reg_a(reg_y)

        # Incrementa el registro contador (PC) de la CPU
        self._cpu.incr_pc(self.BYTES)

        return self.CYCLES


    # Variables privadas
    OPCODE = 0x98
    BYTES = 1
    CYCLES = 2


Instruction.OPCODE_INDEX = {
        # ADC
        0x69: ADC_inmediate,
        0x65: ADC_zero,
        0x75: ADC_zerox,
        0x6D: ADC_abs,
        0x7D: ADC_absx,
        0x79: ADC_absy,
        0x61: ADC_preindexi,
        0x71: ADC_postindexi,
        # AND
        0x29: AND_inmediate,
        0x25: AND_zero,
        0x35: AND_zerox,
        0x2D: AND_abs,
        0x3D: AND_absx,
        0x39: AND_absy,
        0x21: AND_preindexi,
        0x31: AND_postindexi,
        # ASL
        0x0A: ASL_accumulator,
        0x06: ASL_zero,
        0x16: ASL_zerox,
        0x0E: ASL_abs,
        0x1E: AND_absx,
        # BCC
        0x90: BCC,
        # BCS
        0xB0: BCS,
        # BEQ
        0xF0: BEQ,
        # BIT
        0x24: BIT_zero,
        0x2C: BIT_abs,
        # BMI
        0x30: BMI,
        # BNE
        0xD0: BNE,
        # BPL
        0x10: BPL,
        # BRK
        0x00: BRK,
        # BVC
        0x50: BVC,
        # BVS
        0x70: BVS,
        # CLC
        0x18: CLC,
        # CLD
        0xD8: CLD,
        # CLI
        0x58: CLI,
        # CLV
        0xB8: CLV,
        # CMP
        0xC9: CMP_inmediate,
        0xC5: CMP_zero,
        0xD5: CMP_zerox,
        0xCD: CMP_abs,
        0xDD: CMP_absx,
        0xD9: CMP_absy,
        0xC1: CMP_preindexi,
        0xD1: CMP_postindexi,
        # CPX
        0xE0: CPX_inmediate,
        0xE4: CPX_zero,
        0xEC: CPX_abs,
        # CPY
        0xC0: CPY_inmediate,
        0xC4: CPY_zero,
        0xCC: CPY_abs,
        # DEC
        0xC6: DEC_zero,
        0xD6: DEC_zerox,
        0xCE: DEC_abs,
        0xDE: DEC_absx,
        # DEX
        0xCA: DEX,
        # DEY
        0x88: DEY,
        # EOR
        0x49: EOR_inmediate,
        0x45: EOR_zero,
        0x55: EOR_zerox,
        0x4D: EOR_abs,
        0x5D: EOR_absx,
        0x59: EOR_absy,
        0x41: EOR_preindexi,
        0x51: EOR_postindexi,
        # INC
        0xE6: INC_zero,
        0xF6: INC_zerox,
        0xEE: INC_abs,
        0xFE: INC_absx,
        # INX
        0xE8: INX,
        # INY
        0xC8: INY,
        # JMP
        0x4C: JMP_abs,
        0x6C: JMP_indirect,
        # JSR
        0x20: JSR,
        # LDA
        0xA9: LDA_inmediate,
        0xA5: LDA_zero,
        0xB5: LDA_zerox,
        0xAD: LDA_abs,
        0xBD: LDA_absx,
        0xB9: LDA_absy,
        0xA1: LDA_preindexi,
        0xB1: LDA_postindexi,
        # LDX
        0xA2: LDX_inmediate,
        0xA6: LDX_zero,
        0xB6: LDX_zeroy,
        0xAE: LDX_abs,
        0xBE: LDX_absy,
        # LDY
        0xA0: LDY_inmediate,
        0xA4: LDY_zero,
        0xB4: LDY_zerox,
        0xAC: LDY_abs,
        0xBC: LDY_absx,
        # LSR
        0x4A: LSR_accumulator,
        0x46: LSR_zero,
        0x56: LSR_zerox,
        0x4E: LSR_abs,
        0x5E: LSR_absx,
        # NOP
        0xEA: NOP,
        # ORA
        0x09: ORA_inmediate,
        0x05: ORA_zero,
        0x15: ORA_zerox,
        0x0D: ORA_abs,
        0x1D: ORA_absx,
        0x19: ORA_absy,
        0x01: ORA_preindexi,
        0x11: ORA_postindexi,
        # PHA
        0x48: PHA,
        # PHP
        0x08: PHP,
        # PLA
        0x68: PLA,
        # PLP
        0x28: PLP,
        # ROL
        0x2A: ROL_accumulator,
        0x26: ROL_zero,
        0x36: ROL_zerox,
        0x2E: ROL_abs,
        0x3E: ROL_absx,
        # ROR
        0x6A: ROR_accumulator,
        0x66: ROR_zero,
        0x76: ROR_zerox,
        0x6E: ROR_abs,
        0x7E: ROR_absx,
        # RTI
        0x40: RTI,
        # RTS
        0x60: RTS,
        # SBC
        0xE9: SBC_inmediate,
        0xE5: SBC_zero,
        0xF5: SBC_zerox,
        0xED: SBC_abs,
        0xFD: SBC_absx,
        0xF9: SBC_absy,
        0xE1: SBC_preindexi,
        0xF1: SBC_postindexi,
        # SEC
        0x38: SEC,
        # SED
        0xF8: SED,
        # SEI
        0x78: SEI,
        # STA
        0x85: STA_zero,
        0x95: STA_zerox,
        0x8D: STA_abs,
        0x9D: STA_absx,
        0x99: STA_absy,
        0x81: STA_preindexi,
        0x91: STA_postindexi,
        # STX
        0x86: STX_zero,
        0x96: STX_zeroy,
        0x8E: STX_abs,
        # STY
        0x84: STY_zero,
        0x94: STY_zerox,
        0x8C: STY_abs,
        # TAX
        0xAA: TAX,
        # TAY
        0xA8: TAY,
        # TSX
        0xBA: TSX,
        # TXA
        0x8A: TXA,
        # TXS
        0x9A: TXS,
        # TYA
        0x98: TYA,
    }