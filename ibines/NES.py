# -*- coding: utf-8 -*-


from CPU import CPU
from Memory import Memory


class NES(object):

    def __init__(self):
        pass

    ###########################################################################
    # Variables privadas
    ###########################################################################

    # Referencia a la CPU
    cpu = CPU.CPU()

    # Referencia al sistema de memoria
    mem = Memory.Memory()