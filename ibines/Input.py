# -*- coding: utf-8 -*-

# Clase que representa de forma genérica un dispositivo de entrada
class Input(object):
    def __init__(self):
        super(Input, self).__init__()

        self._read_count = 0
        self._write = 0


# Clase que representa un Joypad
class Joypad(Input):
    def __init__(self):
        super(Joypad, self).__init__()

        self._up = 0
        self._down = 0
        self._left = 0
        self._right = 0

        self._a = 0
        self._b = 0

        self._select = 0
        self._start = 0


    # Esta función es la que se usa cuando se lee de memoria el registro correspondiente al joypad
    def read_reg(self):
        if self._read_count == 0:
            v = self._a
        elif self._read_count == 1:
            v = self._b
        elif self._read_count == 2:
            v = self._select
        elif self._read_count == 3:
            v = self._start
        elif self._read_count == 4:
            v = self._up
        elif self._read_count == 5:
            v = self._down
        elif self._read_count == 6:
            v = self._left
        elif self._read_count == 7:
            v = self._right

        self._read_count = (self._read_count + 1) % 8

        return v


    def write_reg(self, v):
        v = v & 0x01
        if v == 0 and self._write == 1:
            self._read_count = 0

        self._write = v


    def set_up(self, v):
        self._up = v


    def set_down(self, v):
        self._down = v


    def set_left(self, v):
        self._left = v


    def set_right(self, v):
        self._right = v


    def set_a(self, v):
        self._a = v


    def set_b(self, v):
        self._b = v


    def set_select(self, v):
        self._selct = v


    def set_start(self, v):
        self._start = v


    def get_up(self):
        return self._up


    def get_down(self):
        return self._down


    def get_left(self):
        return self._left


    def get_right(self):
        return self._right


    def get_a(self):
        return self._a


    def get_b(self):
        return self._b


    def get_select(self):
        return self._select


    def get_start(self):
        return self._start