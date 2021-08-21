# GameSprite Class

import pygame
from level import Object

class GameSprite(Object):
   # Direction constants
   NORTH = 'north'
   SOUTH = 'south'
   EAST = 'east'
   WEST = 'west'

   UP = 'up'
   DOWN = 'down'
   RIGHT = 'right'
   LEFT = 'left'

   def __init__(self, x, y, width, height, num_frames=0, frame_delay=0, direction=RIGHT):     
      super(GameSprite, self).__init__(None, x, y, width, height)

      # Sprite dataz
      self.num_frames = num_frames
      self.frame_delay_ms = frame_delay
      self.direction = direction

      self.images = {self.NORTH: None, self.SOUTH: None, self.EAST: None, self.WEST: None}

      # Used to manage animation, don't touch
      self.current_frame = None

      if self.num_frames > 0:
         self.current_frame_num = self.num_frames
         self.current_frame_delay = self.frame_delay_ms
      else:
         self.current_frame_delay = 0
         self.current_frame_num = 0

   def set_image(self, img):
      """ Set the image of a sprite with no animation. """
      self.current_frame = img

   def set_animation(self, direction, img):
      """ Set a sprite with directional animation. """
      self.images[direction] = img

   def draw(self, surface, offset):
      surface.blit(self.current_frame, offset)

   def update_frame(self, delay):
      if self.num_frames > 0:
         self.current_frame_delay += delay

         if self.current_frame_delay >= self.frame_delay_ms:
            self.current_frame_num += 1

            if self.current_frame_num >= self.num_frames:
               self.current_frame_num = 0

            self.current_frame = self.images[self.direction].subsurface(pygame.Rect(self.current_frame_num * self.width, 0, self.width, self.height))
            self.current_frame_delay = 0

   def force_frame_update(self):
      self.current_frame_num = 0
      self.current_frame_delay = 0
      self.current_frame = self.images[self.direction].subsurface(pygame.Rect(self.current_frame_num * self.width, 0, self.width, self.height))

class GameGroup( pygame.sprite.Group ):
   
   def draw_with_offset(self, surface, x, y):
      """ Draw with an offset """
      for sprite in self.sprites() :
         surface.blit(sprite.image, (sprite.x-x,sprite.y-y), pygame.Rect(0,0,sprite.width,sprite.height))
      
class FireSprite(Object):
   def __init__(self, x, y, width, height, num_frames=0, frame_delay=0, burnratio=0.9) :
      super(FireSprite, self).__init__(None, x, y, width, height)

      # Sprite dataz
      self.num_frames = num_frames
      self.frame_delay_ms = frame_delay
      self.simage = None
      self.image = None
      self.burnratio = burnratio

      # Used to manage animation, don't touch
      self.current_frame = None

      if self.num_frames > 0:
         self.current_frame_num = self.num_frames
         self.current_frame_delay = self.frame_delay_ms
      else:
         self.current_frame_delay = 0
         self.current_frame_num = 0

   def set_image(self, img):
      """ Set the image of a sprite with no animation. """
      self.current_frame = img

   def set_animation(self, img):
      """ Set a sprite with directional animation. """
      self.simage = img
      self.force_frame_update()

   def draw(self, surface, offset):
      surface.blit(self.current_frame, offset)
   
   def update(self, gamescreen, delay):
      beforeframe = self.current_frame_num
      self.update_frame(delay)
      nowframe = self.current_frame_num
      mydamage = 4.0 * (self.burnratio*0.75)
      if(beforeframe != nowframe) :
         temp = pygame.sprite.Sprite()
         temp.rect = pygame.Rect(0,0,48*self.burnratio,48*self.burnratio)
         temp.rect.center = (self.rect.center[0], self.rect.center[1])
         collide = pygame.sprite.spritecollide(temp, gamescreen.level.tile_layers[1], False)
         for sprite in collide :
            if sprite.properties.has_key('health'):
               sprite.properties['health'] = float(sprite.properties['health']) - mydamage
               if sprite.properties.has_key('flashpoint') :
                  flashpoint = float(sprite.properties['flashpoint'])
                  # check to see if we've crossed the flashpoint
                  if sprite.properties['health'] + mydamage >= flashpoint and sprite.properties['health'] < flashpoint : 
                     gamescreen.set_fire(sprite)
               
               # Did you know that humans scream when bears burn them?
               if 'vsl' in sprite.properties:
                  gamescreen.play_random_scream()

               if sprite.properties['health'] <= 0:
                  if sprite.properties.has_key('vsl') :
                     gamescreen.level.vsl_left -= int(sprite.properties['vsl'])
                  if sprite.properties.has_key('traverse') and int(sprite.properties['traverse']) == 1 :
                     sprite.image = pygame.Surface((48,48),pygame.SRCALPHA)
                     del sprite.properties['health']
                     sprite.properties['traverse'] = 0
                  else :
                     sprite.remove(gamescreen.level.tile_layers[1])
                  
                  gamescreen.haveupdates = True
                  #let gamescreen know about our modifications to the tiles

         # If my source is burned up or no longer flammable, burn out
         if ((self.mysource.properties.has_key('health') and self.mysource.properties['health'] <= 0) or
            self.mysource.properties.has_key('health') == False): 
            gamescreen.fires.remove(self)
   
   def update_frame(self, delay):
      if self.num_frames > 0:
         self.current_frame_delay += delay

         if self.current_frame_delay >= self.frame_delay_ms:
            self.current_frame_num += 1

            if self.current_frame_num >= self.num_frames:
               self.current_frame_num = 0

            self.current_frame = self.simage.subsurface(pygame.Rect(self.current_frame_num * self.width, 0, self.width, self.height))
            self.image = self.current_frame
            self.current_frame_delay = 0

   def force_frame_update(self):
      self.current_frame_num = 0
      self.current_frame_delay = 0
      self.current_frame = self.simage.subsurface(pygame.Rect(self.current_frame_num * self.width, 0, self.width, self.height))
      self.image = self.current_frame
