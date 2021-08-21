import pygame, sys, os
from pygame.locals import *

pygame.font.init()

def load_font(name, size, bold=False, italic=False):
   font = None

   # Attempt to load system fonts first, then local
   path = pygame.font.match_font(name, bold, italic)

   if path:
      font = pygame.font.Font(path)
   else:
      path = os.path.join('fonts', name)
      font = pygame.font.Font(path, size)

   return font

image_cache = {}
def load_image(image_name, folder='sprites'):
   path = os.path.join(folder, image_name)

   if path in image_cache:
      return image_cache[path]
   else:
      img = pygame.image.load(path).convert_alpha()
      image_cache[path] = img
      return img

def map_value(val, in_min, in_max, out_min, out_max):
   result = (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min 
   return result
   
def load_levels():
   levels = []

   for filename in open(os.path.join('levels', 'list.txt')):
      levels.append(filename.strip())

   levels.append(None)

   return levels
