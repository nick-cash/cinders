# Game-specific level stuffs

import pygame, math, random
import level

class GameLevel(level.Level):
   # Time left in milliseconds

   def __init__(self, lvl):
      # Time left in milliseconds
      self.time_left = 0
      # Value of Statistical Lives left for victory
      self.vsl_left = 1000
      self.border_ground = "29"
      self.border_block = "49"
      super(GameLevel, self).__init__(lvl)
   
   def fill_surface(self, surface, list_of_gids) :
      """ Fills a surface with randomly selected tile images from a list."""
      x = 0
      y = 0
      while y < surface.get_height() :
         gid = int(random.choice(list_of_gids))
         surface.blit(self.tile_images[gid], (x, y))
         x = x + self.tile_images[gid].get_width()
         if x > surface.get_width() :
            y = y + self.tile_images[gid].get_height()
            x = 0
      
   def post_process(self):
      SRCALPHA = pygame.SRCALPHA
      if 'timer' in self.properties:
         self.time_left = int(self.properties['timer'])
      if 'destroy_vsl' in self.properties:
         self.vsl_left = int(self.properties['destroy_vsl'])
      if 'border_ground' in self.properties and 'border_block' in self.properties :
         self.border_ground = self.properties['border_ground']
         self.border_block = self.properties['border_block']
      
      groundgids = self.border_ground.split('-')
      blockgids = self.border_block.split('-')
      
      #make the ground "tile" sprites
      gtop = level.Tile(pygame.Surface( ((self.width+28) * self.tile_width, 384)), 14*self.tile_width*-1, -384)
      gbottom = level.Tile(pygame.Surface( ((self.width+28) * self.tile_width, 384)),
         14*self.tile_width*-1, self.height * self.tile_height)
      gleft = level.Tile(pygame.Surface( (14 * self.tile_width, self.height * self.tile_height)), 14*self.tile_width*-1, 0)
      gright = level.Tile(pygame.Surface( (14 * self.tile_width, self.height * self.tile_height)), self.width*self.tile_width, 0)

      #make the blocking "tile" sprites
      btop = level.Tile(pygame.Surface(((self.width+28) * self.tile_width, 384), SRCALPHA), 14*self.tile_width*-1, -384)
      bbottom = level.Tile(pygame.Surface(((self.width+28) * self.tile_width, 384 ), SRCALPHA),
         14*self.tile_width*-1, self.height * self.tile_height)
      bleft = level.Tile(pygame.Surface( (14 * self.tile_width, self.height * self.tile_height), SRCALPHA), 14*self.tile_width*-1, 0)
      bright = level.Tile(pygame.Surface( (14 * self.tile_width, self.height * self.tile_height), SRCALPHA), self.width*self.tile_width, 0)
      
      self.fill_surface(gtop.image, groundgids)
      self.fill_surface(gbottom.image, groundgids)
      self.fill_surface(gleft.image, groundgids)
      self.fill_surface(gright.image, groundgids)

      self.fill_surface(btop.image, blockgids)
      self.fill_surface(bbottom.image, blockgids)
      self.fill_surface(bleft.image, blockgids)
      self.fill_surface(bright.image, blockgids)
      
      self.tile_layers[0].add(gtop)
      self.tile_layers[0].add(gbottom)
      self.tile_layers[0].add(gleft)
      self.tile_layers[0].add(gright)
      
      self.tile_layers[1].add(btop)
      self.tile_layers[1].add(bbottom)
      self.tile_layers[1].add(bleft)
      self.tile_layers[1].add(bright)
      
