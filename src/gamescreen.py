import pygame, sys, os, time, math, random
import screen
import utilities

from sound_manager import SoundManager
from gamelevel import GameLevel
from sprite import GameSprite
from sprite import FireSprite
from sprite import GameGroup
from pygame.locals import *

class GameScreen(screen.Screen):
   """ Base screen class, expand """

   def __init__(self):
      """ Default screen constructor, creates a new clock """
      super(GameScreen, self).__init__()

      self.req_fps = 48 # Just like TEH HOBBITZ
      self.sound_manager = SoundManager()

      #GameScreen variables
      self.level = None
      self.draw_offset = pygame.Rect(0,0,1024,768)
      self.cache_area = pygame.Rect(0,0,1024+432,768+432)
      self.cache_surface = pygame.Surface((self.cache_area.width, self.cache_area.height))

      self.clock = pygame.time.Clock();
      self.clock_tick()

      self.font_lato = utilities.load_font(os.path.join('lato','Lato-Bold.ttf'), 32)
      self.font_flame = utilities.load_font('Flame.ttf', 32)

   def update_draw_offset(self):
      self.draw_offset.center = (self.cinders.x, self.cinders.y)

   def load_level(self, lvl):
      """ Load a level from the file with the given name. """
      self.level = GameLevel(lvl)

      for object in self.level.objects:
         if 'type' in object:
            if object['type'] == 'Cinders':
               self.cinders = GameSprite(object['x'], object['y'], 48, 48, 2, 500)
               self.cinders.direction = GameSprite.RIGHT
               self.update_draw_offset()
               self.draw_cache()

               self.cinders.set_animation(GameSprite.UP, utilities.load_image('cinders-up.png'))
               self.cinders.set_animation(GameSprite.DOWN, utilities.load_image('cinders-down.png'))
               self.cinders.set_animation(GameSprite.LEFT, utilities.load_image('cinders-left.png'))
               self.cinders.set_animation(GameSprite.RIGHT, utilities.load_image('cinders-right.png'))

      self.fireball = {'x': 0, 'y': 0}
      self.flamethrower_state = None
      self.flamethrower_event_at = None
      self.flamethrower_frame_function = None
      self.fires = GameGroup([])

      # Sound shiz
      self.ambientfire = None
      self.flamethrower_noise = None
      self.happyroar = 0
      self.screamtimer = 0

   def play_random_scream(self):
      if self.screamtimer <= 0:
         screams = ['aarrgghh.wav', 'ahhhhhh.wav', 'female_scream.wav', 'female_scream2.wav']
         self.sound_manager.play_sound(random.choice(screams), volume=0.2)

         self.screamtimer = 3000
      else:
         self.screamtimer -= self.tick_time

   def set_fire(self, sprite):
      """ Set a tile on fire, returns fire sprite """
      if sprite.properties.has_key('burnratio') :
         burnratio = float(sprite.properties['burnratio'])
      else :
         burnratio = 1.1
         
      fire = FireSprite(sprite.x, sprite.y, 48, 48, 3, 250, burnratio)
      fire.mysource = sprite
      fire.set_animation(utilities.load_image('burning.png'))
      self.fires.add(fire)

   def input(self, events):
      """ Input function to override, call self.default_event_handler 
      if it is not None for events you don't want to handle."""

      for event in events:
         if event.type == KEYUP and event.key == K_ESCAPE:
            return "switch-to-pause"
         else:
            if self.default_event_handler != None:
               self.default_event_handler([event])

   def direction_shift_by_vector(self, sourceRect, direction, vector):
      if direction == GameSprite.LEFT:
         return sourceRect.move(-vector[0], 0)
      elif direction == GameSprite.RIGHT:
         return sourceRect.move(vector[0], 0)
      elif direction == GameSprite.UP:
         return sourceRect.move(0, -vector[1])
      elif direction == GameSprite.DOWN:
         return sourceRect.move(0, vector[1])

   
   bar_width = 150
   view_width = 1024
   def can_and_should_show_flames(self, space):
      #print self.flamethrower_state

      now = pygame.time.get_ticks()
      charge_ms = 1000
      drain_ms = 2000
      if not space:
         self.flamethrower_noise = None
         self.sound_manager.stop_sound('flamethrower.ogg', fadeout=1000)

         if self.flamethrower_state == 'empty':
            self.flamethrower_state = 'charge'
            self.flamethrower_event_at = now
            self.flamethrower_frame_function = lambda new_now: utilities.map_value(new_now, now, now + charge_ms, self.view_width, self.view_width - self.bar_width)
         elif self.flamethrower_state == 'charge':
            stop_time = self.flamethrower_event_at + charge_ms
            if (stop_time < now):
               self.flamethrower_event_at = None
               self.flamethrower_state = None
         elif self.flamethrower_state == 'drain':
            percentage = utilities.map_value(self.flamethrower_frame_function(now), self.view_width - self.bar_width, self.view_width, float(1), float(0))
            ms_offset = percentage * charge_ms
            ms_origin = now - ms_offset
            self.flamethrower_frame_function = lambda new_now: utilities.map_value(new_now, ms_origin, ms_origin + charge_ms, self.view_width, self.view_width - self.bar_width)
            self.flamethrower_event_at = ms_origin
            self.flamethrower_state = 'charge'
         elif self.flamethrower_state == None:
            self.flamethrower_frame_function = lambda new_now: self.view_width - self.bar_width
            self.flamethrower_event_at = None
            self.flamethrower_state = None
         return False

      if self.flamethrower_state == 'empty':
         self.sound_manager.play_sound('grizzlybear2-short.wav', volume=0.1, fade_ms=100)
         return False
      elif self.flamethrower_state == 'charge':
         percentage = utilities.map_value(self.flamethrower_frame_function(now), self.view_width - self.bar_width, self.view_width, float(0), float(1))
         ms_offset = percentage * drain_ms
         ms_origin = now - ms_offset
         self.flamethrower_frame_function = lambda new_now: utilities.map_value(new_now, ms_origin, ms_origin + drain_ms, self.view_width - self.bar_width, self.view_width)
         self.flamethrower_event_at = ms_origin
         self.flamethrower_state = 'drain'
         return False
      elif self.flamethrower_state == None:
         self.flamethrower_event_at = now
         self.flamethrower_state = 'drain'
         self.flamethrower_frame_function = lambda new_now: utilities.map_value(new_now, now, now + drain_ms, self.view_width - self.bar_width, self.view_width)
      elif self.flamethrower_state == 'drain':
         stop_time = self.flamethrower_event_at + drain_ms
         if (stop_time < now):
            self.flamethrower_state = 'empty'

      return True

   def draw_flame_bar(self, screensurface):
      x = self.flamethrower_frame_function(pygame.time.get_ticks())
      #print "{} {}".format(self.flamethrower_state, x)
      pygame.draw.rect(screensurface, (255, 0, 0), pygame.Rect(x, 0, self.bar_width, 20))

   def direction_clockwise_to_direction(self, direction):
      directions = {
         GameSprite.LEFT: GameSprite.UP,
         GameSprite.UP: GameSprite.RIGHT,
         GameSprite.RIGHT: GameSprite.DOWN,
         GameSprite.DOWN: GameSprite.LEFT,
      }
      return directions[direction]

   def update_and_draw_flames(self, key, screensurface):
      draw_flames = self.can_and_should_show_flames(key[pygame.K_SPACE])

      # Showin flames, so play dat firey noise
      if draw_flames and not self.flamethrower_noise:
         self.flamethrower_noise = self.sound_manager.play_sound('flamethrower.ogg', volume=0.2)

      self.draw_flame_bar(screensurface)
      if not draw_flames:
         return
      
      updaterender = False

      self.fireball_image = utilities.load_image('flame-{}.png'.format(self.cinders.direction))
      #base it on length of blast
      x = self.flamethrower_frame_function(pygame.time.get_ticks())-924
      framenum = min(int(math.ceil((float(x)/75)*5)), 5) - (int(x)&1)
      fire_dpms = 1 + (float(framenum)*1.5)
      frame = self.direction_shift_by_vector(pygame.Rect(self.cinders.x, self.cinders.y, 48, 48), self.cinders.direction, (48, 48))
      frame = self.direction_shift_by_vector(frame, self.direction_clockwise_to_direction(self.cinders.direction), (10,10))
      self.fireball['x'] = frame.x
      self.fireball['y'] = frame.y
      screensurface.blit(self.fireball_image, 
         (self.fireball['x']-self.draw_offset.left, self.fireball['y']-self.draw_offset.top),
         pygame.Rect(framenum*48,0,48,48))

      fireball_sprite = pygame.sprite.Sprite()
      fireball_sprite.rect = pygame.Rect(self.fireball['x'], self.fireball['y'], 48,48)

      collided = pygame.sprite.spritecollide(fireball_sprite, self.level.tile_layers[1], False)
      
      # Let out a gleeful roar at the destruction on occasion
      if len(collided) > 0 and self.happyroar <= 0:
         self.happyroar = random.randint(2000, 3000)
         self.sound_manager.play_sound('grizzlybear1-short.wav', volume=0.1, fade_ms=400)
      else:
         self.happyroar -= self.tick_time

      for sprite in collided:
         if not sprite.properties.has_key('health'):
            continue

         health = float(sprite.properties['health'])
         health -= fire_dpms
         sprite.properties['health'] = health

         if sprite.properties.has_key('flashpoint') :
            flashpoint = float(sprite.properties['flashpoint'])
            # check to see if we'vecrossed the flashpoint
            if health + fire_dpms >= flashpoint and health < flashpoint : 
               self.set_fire(sprite)

         # When a bear with a flamethrower starts to burn you, you scream.
         if 'vsl' in sprite.properties:
            self.play_random_scream()
       
         if health <= 0:
            if sprite.properties.has_key('vsl') :
               self.level.vsl_left -= int(sprite.properties['vsl'])
            if sprite.properties.has_key('traverse') and int(sprite.properties['traverse']) == 1 :
               sprite.image = pygame.Surface((48,48),pygame.SRCALPHA)
               del sprite.properties['health']
               sprite.properties['traverse'] = 0
            else:
               sprite.remove(self.level.tile_layers[1])

            #this health <= 0 chunk is duplicated in FireSprite
            # So make sure to update FireSprite if you modify this.
            updaterender = True

      if updaterender:
         self.draw_cache()

   def update_direction(self, deltax, deltay):
      old_dir = self.cinders.direction

      if deltax > 0:
         self.cinders.direction = GameSprite.RIGHT
      elif deltax < 0:
         self.cinders.direction = GameSprite.LEFT
      elif deltay > 0:
         self.cinders.direction = GameSprite.DOWN
      elif deltay < 0:
         self.cinders.direction = GameSprite.UP

      if old_dir != self.cinders.direction:
         self.cinders.force_frame_update()

   def sprite_not_traversable(self, sprite) :
      """ returns true if a sprite is not traversable """
      if(sprite.properties.has_key('traverse')) :
         if int(sprite.properties['traverse']) == 1 :
            return False
         else :
            return True
      else :
         return True

   def update_and_draw_cinders(self, key, screensurface):
      spd = 3 #for now, movement is by frame
      cspdx = 0
      cspdy = 0
      #for now, expect blocking/interactable tiles to be on Tile Layer 2
            
      if key[pygame.K_a] : cspdx -= spd
      if key[pygame.K_d] : cspdx += spd
      if key[pygame.K_LEFT] : cspdx -= spd
      if key[pygame.K_RIGHT] : cspdx += spd
      if key[pygame.K_w] : cspdy -= spd
      if key[pygame.K_s] : cspdy += spd
      if key[pygame.K_UP] : cspdy -= spd
      if key[pygame.K_DOWN] : cspdy += spd

      if cspdx == 0 and cspdy != 0 or cspdx != 0 and cspdy == 0:
         self.update_direction(cspdx, cspdy)

      #if we already intersect a non-traversable block, trigger loss message
      self.cinders.rect = pygame.Rect(self.cinders.x+2, self.cinders.y+2, 44,44)
      collided = pygame.sprite.spritecollide(self.cinders, self.level.tile_layers[1], False)
      collided = filter(self.sprite_not_traversable, collided)
      for tile in collided :
         intersect = tile.rect.clip(self.cinders.rect)
         if(intersect.width > 3 or intersect.height > 3) :
            self.causedeath = True

      self.cinders.x += cspdx
      self.cinders.rect = pygame.Rect(self.cinders.x+2, self.cinders.y+2, 44,44)
      collided = pygame.sprite.spritecollide(self.cinders, self.level.tile_layers[1], False)
      collided = filter(self.sprite_not_traversable, collided)
      
      #moved horizontally, check for collision
      if(len(collided)):
         #moving left
         if(cspdx < 0):
            self.cinders.x = collided[0].rect.right - 2
         elif(cspdx > 0):
            self.cinders.x = collided[0].rect.x - 46

      #now perform vertical move
      self.cinders.y += cspdy
      self.cinders.rect = pygame.Rect(self.cinders.x+2, self.cinders.y+2, 44,44)
      collided = pygame.sprite.spritecollide(self.cinders, self.level.tile_layers[1], False)
      collided = filter(self.sprite_not_traversable, collided)
      if(len(collided)):
         #moving up
         if(cspdy < 0):
            self.cinders.y = collided[0].rect.bottom
         elif(cspdy > 0):
            self.cinders.y = collided[0].rect.y - 48

      # Update frame and draw
      self.cinders.update_frame(self.tick_time)
      self.cinders.draw(screensurface, (self.cinders.x-self.draw_offset.left,
         self.cinders.y-self.draw_offset.top))

   def draw_cache(self):
      self.cache_area.center = (self.cinders.x, self.cinders.y)
      cachesprite = pygame.sprite.Sprite()
      cachesprite.rect = self.cache_area
      self.cache_surface.fill((0,64,0))
      for tile_layer in self.level.tile_layers:
         collide = pygame.sprite.spritecollide(cachesprite, tile_layer, False)
         for sprite in collide :
            self.cache_surface.blit(sprite.image, (sprite.rect.x-self.cache_area.left,
               sprite.rect.y-self.cache_area.top))

   def update(self, screensurface):
      """ Convenient hook to plug screen updates into,
      doesn't actually do anything without being overridden,
      remember to call clock tick in your update implementation,
      pass it your screen surface for the drawatage.  Return some
      game specific logic for switching or ending or what have you."""

      self.clock_tick()
      #Lazy way to let other things cause a level loss.
      self.causedeath = False
      #Handle Input
      result = self.input(pygame.event.get())
      screensurface.fill((0,0,0))

      # Update timer if present, render in preparation for blit
      rendered_countdown = None

      if not self.paused and self.level.time_left > 0:
         self.level.time_left -= self.tick_time

         if self.level.time_left <= 0:
            self.level.time_left = 0         
            return "level-failure"

         text = "%.1f" % (self.level.time_left / 1000.0)
         rendered_countdown = self.font_lato.render(text, True, (240, 240, 240))
      
      rendered_vsl_remaining = None
      text = "Burn %d More Humans" % (self.level.vsl_left)
      rendered_vsl_remaining = self.font_flame.render(text, True, (240, 240, 240))      
      
      # Update VSL countdown, it's always present.  It is an error condition not
      # to provide one at this point in time.
      if self.level.vsl_left <= 0:
         return "level-success"
      
      # BURNINATE
      self.haveupdates = False
      self.fires.update(self, self.tick_time)

      if len(self.fires.sprites()) > 0:
         if not self.ambientfire:
            self.ambientfire = self.sound_manager.play_sound('forest_fire2.wav', volume=0.1, loop=-1)
      else:
         self.sound_manager.stop_sound('forest_fire2.wav', fadeout=2000)
         self.ambientfire = None

      if self.haveupdates == True:
         self.draw_cache()
      
      # Render screen
      if(self.cache_area.contains(self.draw_offset) == False) :
         self.draw_cache()

      screensurface.blit(self.cache_surface, (0-(self.draw_offset.left - self.cache_area.left),
         0-(self.draw_offset.top - self.cache_area.top)))

      # Handle objects
      key = pygame.key.get_pressed()
      self.update_and_draw_cinders(key, screensurface)
      self.update_and_draw_flames(key, screensurface)            

      #draw fires
      self.fires.draw_with_offset(screensurface, self.draw_offset.left, self.draw_offset.top)

      # Draw timer if applicable
      if rendered_countdown:
         screensurface.blit(rendered_countdown, (512 - (rendered_countdown.get_width() / 2), 5))
      screensurface.blit(rendered_vsl_remaining, (20, 5))
      self.update_draw_offset()
      
      if self.causedeath == True:
         return "level-failure"
      
      return result
