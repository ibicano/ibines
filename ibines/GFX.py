# -*- coding: utf-8 -*-

import pygame
import time

"""
GFX

Implementa el motor gráfico para pintar la salida a pantalla. La
implementación inicial utiliza SDL a través de PyGame.
"""
class GFX(object):

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



#gfx = GFX()
#gfx.run()
