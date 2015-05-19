# -*- coding: utf-8 -*-

#import pygame
import sdl2.ext
import time

"""
GFX

Implementa el motor gráfico para pintar la salida a pantalla. La
implementación inicial utiliza SDL a través de PyGame.
"""

class GFX(object):
    def __init__(self):
        pass

    def draw_pixel(self, x, y, color=(0, 0, 0)):
        pass

    def fill(self, color=(0, 0, 0)):
        pass

    def update(self):
        pass


class GFX_Pygame(GFX):

    def __init__(self):
        ###########################################################################
        # Variables de instancia
        ###########################################################################
        self._screen = None
        self._pixels = None
        ###########################################################################
        ###########################################################################

        pygame.display.init()
        self._screen = pygame.display.set_mode((256, 240))
        self._screen.fill((0,0,0))
        self._pixels = pygame.PixelArray(self._screen)


    def draw_pixel(self, x, y, color=(0, 0, 0)):
        self._pixels[x][y] = self._screen.map_rgb(color)


    def fill(self, color=(0, 0, 0)):
        self._screen.fill(color)


    def update(self):
        pygame.display.update()


    def run(self):
        while 1:
            self._screen.fill((255,0,0))
            #for x in range(len(self._pixels)):
                #for y in range(len(self._pixels[x])):
                    #if (x % 2) == 0:
                        #if (y % 2) != 0:
                            #self._pixels[x][y] = self._screen.map_rgb((0,0,255))
                    #elif (x % 2) != 0:
                        #if (y % 2) == 0:
                            #self._pixels[x][y] = self._screen.map_rgb((0,0,255))

            self._pixels[50:100,20:200] = self._screen.map_rgb((0,0,255))

            pygame.display.update()
            time.sleep(0.04)


class GFX_PySdl2(GFX):

    def __init__(self):
        self._window = sdl2.ext.Window("Ventana", size=(256, 240))
        self._surface = self._window.get_surface()
        self._pixels = sdl2.ext.PixelView(self._surface)
        self.fill((0, 0, 0))
        self._window.show()

        # Buffer para mejorar el rendimiento.
        # Los pixels se escriben a este buffer con un flag que indica si su valor
        # ha cambiado respecto al valor anterior, de tal forma que se pintan cuando
        # se ejecuta la función "update()" sólo si se han modificado.
        self._buffer = [None] * 256
        for x in range(256):
            self._buffer[x] = [None] * 256

        for x in range(256):
            for y in range(240):
                self._buffer[x][y] = {"color": (0, 0, 0), "modified": 0}


    def draw_pixel(self, x, y, color=(0, 0, 0)):
        if self._buffer[x][y]["color"] != color:
            self._buffer[x][y]["color"] = color
            self._buffer[x][y]["modified"] = 1
        else:
            self._buffer[x][y]["modified"] = 0


    def fill(self, color):
        sdl2.ext.fill(self._surface, sdl2.ext.COLOR(color))


    def update(self):
        for x in range(256):
            for y in range(240):
                if self._buffer[x][y]["modified"]:
                    self._pixels[y][x] = sdl2.ext.COLOR(self._buffer[x][y]["color"])
        self._window.refresh()