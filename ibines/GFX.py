# -*- coding: utf-8 -*-

import pygame
import time

class GFX(object):

    def __init__(self):
        pygame.display.init()
        self._screen = pygame.display.set_mode((640, 480))
        self._screen.fill((255,0,0))
        self._pixels = pygame.PixelArray(self._screen)

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


    _screen = None
    _pixels = None


gfx = GFX()
gfx.run()
