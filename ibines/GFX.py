# -*- coding: utf-8 -*-

#import pygame
import sdl2.ext
import time
from sdl2 import *
from ctypes import *

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

    def clear(self):
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
        self._window = SDL_CreateWindow("Ventana", 0, 0, 256, 240, 0)
        self._surface = SDL_CreateRGBSurface(0, 256, 240, 32, 0, 0, 0, 0)
        self._pixel_format = self._surface.contents.format
        self._renderer = SDL_CreateRenderer(self._window, -1, SDL_RENDERER_ACCELERATED)

        self._texture = SDL_CreateTextureFromSurface(self._renderer, self._surface)

        self._pixels = (c_uint32 * 61440)()

        SDL_UpdateTexture(self._texture, None, self._pixels, 1024)
        SDL_RenderCopy(self._renderer, self._texture, None, None)
        SDL_RenderPresent(self._renderer)


    def draw_pixel(self, x, y, color=(0, 0, 0)):
        p = (y * 256) + x
        self._pixels[p] = SDL_MapRGBA(self._pixel_format, color[0], color[1], color[2], 0)


    def fill(self, color):
        pass


    def clear(self):
        SDL_RenderClear(self._renderer)


    def update(self):
        SDL_UpdateTexture(self._texture, None, self._pixels, 1024)
        SDL_RenderCopy(self._renderer, self._texture, None, None)
        SDL_RenderPresent(self._renderer)
