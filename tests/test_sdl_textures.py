from sdl2 import *
import time
from ctypes import *

print "Hola mundo"

SDL_Init(SDL_INIT_VIDEO)

window = SDL_CreateWindow("Prueba",  SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 640, 480, 0)
renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)

surface = SDL_CreateRGBSurface(0, 640, 480, 32, 0, 0, 0, 0)
SDL_FillRect(surface, None, SDL_MapRGB(surface.contents.format, 0, 255, 0))

#texture = SDL_CreateTextureFromSurface(renderer, surface.contents)
texture = SDL_CreateTexture(renderer, surface.contents.format.contents.format, SDL_TEXTUREACCESS_STATIC, 640, 480)


SDL_UpdateTexture(texture, None, surface.contents.pixels, 2560)
SDL_RenderCopy(renderer, texture, None, None)

color = 0

t1 = time.time()
t2 = 0
frames = 0
counter = 0

while 1:
    
    if color == 0:
        SDL_FillRect(surface, None, SDL_MapRGB(surface.contents.format, 255, 0, 0))
        color = 1
    else:
        SDL_FillRect(surface, None, SDL_MapRGB(surface.contents.format, 0, 0, 255))
        color = 0
        
    verde = SDL_MapRGB(surface.contents.format, 0, 255, 0)
    pixels = (c_uint32 * 307200)()
    
    for i in range(107200):
        pixels[i] = verde
        
    SDL_UpdateTexture(texture, None, pixels, 2560)
    SDL_RenderCopy(renderer, texture, None, None)
    
    
        
    SDL_RenderPresent(renderer)
    
    
    if t2 >= 1:
        print str(int(frames/t2)) + " fps"
        frames = 0
        t1 = time.time()
        t2 = 0
    
    t2 = time.time() - t1
    frames += 1
    
    counter += 1