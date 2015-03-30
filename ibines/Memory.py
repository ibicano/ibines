# -*- coding: utf-8 -*-


class Memory(object):

    # Constructor
    def __init__(self):
        pass

    # Devuelve el contenido de una posición de memoria
    def read_data(self, addr):
        pass

    # Establece el contenido de una posición de memoria
    def write_data(self, data, addr):
        pass


    ###########################################################################
    # Variables privadas
    ###########################################################################

    # Array para almacenar el contenido de la memoria
    memory = []