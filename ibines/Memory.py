# -*- coding: utf-8 -*-


class Memory(object):

    # Constructor
    def __init__(self):
        pass

    # Devuelve el contenido de una posición de memoria
    def getData(self, addr):
        pass

    # Establece el contenido de una posición de memoria
    def setData(self, data, addr):
        pass


    ###########################################################################
    # Variables privadas
    ###########################################################################

    # Array para almacenar el contenido de la memoria
    memory = []