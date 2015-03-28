# -*- coding: utf-8 -*-


from CPU import CPU
from Memory import Memory
from Instruction import *


class NES(object):

    def __init__(self):
        pass

    ###########################################################################
    # Variables privadas
    ###########################################################################


    # Referencia a la CPU
    cpu = CPU()

    adc = ADC_inmediate([0x00], cpu)

    # Referencia al sistema de memoria
    mem = Memory.Memory()