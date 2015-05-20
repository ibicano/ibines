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
        self._surface = SDL_GetWindowSurface(self._window)
        self._pixel_format = self._surface.contents.format
        self._renderer = SDL_CreateRenderer(self._window, -1, SDL_RENDERER_ACCELERATED)



        #self._texture = SDL_CreateTexture(self._renderer, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STATIC, 256, 240)
        self._texture = SDL_CreateTextureFromSurface(self._renderer, self._surface)

        '''
        array_pixels = c_uint32 * 61440
        self._pixels = array_pixels()

        for x in range(61440):
            p = SDL_MapRGBA(self._pixel_format, 0, 0, 0, 255)
            self._pixels[x] = p
        '''
        self._pixels = ""
        for x in range(61440):
            self._pixels += 'd'
            self._pixels += 'd'
            self._pixels += 'd'
            self._pixels += 'd'


        SDL_UpdateTexture(self._texture, None, cast(c_char_p(self._pixels), c_void_p), c_int(0))
        SDL_RenderCopy(self._renderer, self._texture, None, None)
        SDL_RenderPresent(self._renderer)

    def draw_pixel(self, x, y, color=(0, 0, 0)):
        pass


    def fill(self, color):
        pass


    def clear(self):
        SDL_RenderClear(self._renderer)


    def update(self):
        SDL_UpdateTexture(self._texture, None, cast(c_char_p(self._pixels), c_void_p), c_int(0))
        #SDL_UnlockTexture(self._texture)

        SDL_RenderPresent(self._renderer)
        #SDL_RenderClear(self._renderer)
        #SDL_LockTexture(self._texture, None, self._pixels, c_int(0))