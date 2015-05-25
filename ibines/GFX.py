# -*- coding: utf-8 -*-

import sdl2.ext
import time
import array
from sdl2 import *
from ctypes import *

"""
GFX

Implementa el motor gráfico para pintar la salida a pantalla. La
implementación inicial utiliza SDL a través de PyGame.
"""

class GFX(object):
    def __init__(self):
        self._viewport_width = 256
        self._viewport_height = 240

    def draw_pixel(self, x, y, color=(0, 0, 0)):
        pass

    def fill(self, color=(0, 0, 0)):
        pass

    def clear(self):
        pass

    def update(self):
        pass


class GFX_PySdl2(GFX):

    def __init__(self):
        super(GFX_PySdl2, self).__init__()
        
        # Objeto SDL de la ventana
        self._window = SDL_CreateWindow("Ventana", 0, 0, self._viewport_width, self._viewport_height, 0)

        # Crea una superficie para inicializar la textura
        self._surface = SDL_CreateRGBSurface(0, 256, 240, 32, 0, 0, 0, 0)

        # Formato del pixel tomado de la superficie inicializada automáticamente
        self._pixel_format = self._surface.contents.format

        # Renderizador
        self._renderer = SDL_CreateRenderer(self._window, -1, SDL_RENDERER_ACCELERATED)

        # Textura que almacenará la información de los pixels
        self._texture = SDL_CreateTextureFromSurface(self._renderer, self._surface)

        # Información de los pixeles. Almacena los pixeles en un array líneal en el que cada
        # posición es un píxel representado por un entero de 32 bits en formato ARGB
        self._pixels = array.array("I", [0] * 61440)

        # Actualiza la textura con el array de pixeles. El último parámetro es el número
        # de bytes que tiene una lñínea hortizontal (256*4=1024)
        SDL_UpdateTexture(self._texture, None, self._pixels.buffer_info()[0], 1024)

        # Copia la textura al renderizador
        SDL_RenderCopy(self._renderer, self._texture, None, None)

        # Renderiza la pantalla
        SDL_RenderPresent(self._renderer)


    def draw_pixel(self, x, y, color=(0, 0, 0)):
        # Calcula la posición x,y del pixel en el array lineal de pixeles
        p = (y << 8) | x

        v = 0xFF000000 | color[0] << 16 | color[1] << 8 | color[2]

        # Asigna el valos del pixel como un entero de 32 bits con formato ARGB
        self._pixels[p] = v


    def fill(self, color):
        v = 0xFF000000 | color[0] << 16 | color[1] << 8 | color[2]
        for p in xrange(len(self._pixels)):
            self._pixels[p] = v


    def clear(self):
        SDL_RenderClear(self._renderer)


    def update(self):
        SDL_UpdateTexture(self._texture, None, self._pixels.buffer_info()[0], 1024)
        SDL_RenderCopy(self._renderer, self._texture, None, None)
        SDL_RenderPresent(self._renderer)
