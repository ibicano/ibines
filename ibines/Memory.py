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
    # Se escribe en todas las posiciones de las que se hace mirror. Sería más
    # eficiente no escribir todas y mapear las posiciones en una soloa
    # OPTIMIZE: Lo expuesto anteriormente
    def write_data(self, data, addr):
        a = addr & 0xFFFF
        d = data & 0xFF

        if a >= 0x000 and a <= 0x1FFF:
            n = a % 0x800
            self._memory[n] = d
            self._memory[0x0800 + n] = d
            self._memory[0x1000 + n] = d
            self._memory[0x1800 + n] = d
        elif a >= 0x2000 and a <= 0x3FFF:
            #escribe en todas las pociones "espejo"
            x = 0
            while x < 0x0400:
                n = a % 0x08 + (x * 0x08)
                self._memory[n] = d
                x += 1
        else:
            self._memory[a] = d


    ###########################################################################
    # Variables privadas
    ###########################################################################

    # Array para almacenar el contenido de la memoria
    _memory = []