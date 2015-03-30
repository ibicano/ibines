# -*- coding: utf-8 -*-


class Memory(object):

    # Constructor
    def __init__(self):
        pass

    # Devuelve el contenido de una posición de memoria
    def read_data(self, addr):
        a = addr & 0xFFFF
        return self._memory[a]

    # Establece el contenido de una posición de memoria
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF
        self._memory[a] = d


    ###########################################################################
    # Variables privadas
    ###########################################################################

    # Array para almacenar el contenido de la memoria
    _memory = []