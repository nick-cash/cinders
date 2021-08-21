import pygame, sys, os, time, math, random
import screen
import utilities

from pygame.locals import *

class CreditScreen(screen.Screen):
   """ Base screen class, expand """

   def __init__(self):
      """ Default screen constructor, creates a new clock """
      super(CreditScreen, self).__init__()

      self.flip_time = 5000
      self.curr_delay = self.flip_time

      self.font_flame = utilities.load_font('Flame.ttf', 32)

      self.credit_index = 0
      self.credit_images = [
         utilities.load_image('credits-brian.jpg', 'graphics'),
         utilities.load_image('credits-nick.jpg', 'graphics'),
         utilities.load_image('credits-allyn.jpg', 'graphics'),
         utilities.load_image('credits-kerry-jess.jpg', 'graphics'),
         utilities.load_image('credits-misc.jpg', 'graphics')
      ]

      self.credit_index_end = len(self.credit_images)
      self.draw = True

      self.press_escape_surface = self.font_flame.render("ESC for main menu", True, (240, 240, 240))

   def pause_clock(self):
      """ Pause this screen's clock, basically tells update
       to ignore ticks """
      
      self.paused = True

   def unpause_clock(self):
      self.clock_tick()
      self.paused = False
      self.clock_tick()

   def clock_tick(self):
      """ Runs the screen's clock tick and updates accumulated time """
      
      millesecond = self.clock.tick(self.req_fps)

      if self.paused:
         self.accumulated_time = self.accumulated_time
      else:
         self.lasttime = self.accumulated_time
         self.accumulated_time += millesecond
         self.tick_time = self.accumulated_time - self.lasttime
 
   def input(self, events):
      """ Input function to override, call self.default_event_handler 
      if it is not None for events you don't want to handle."""
      
      for event in events:
         if event.type == KEYUP and event.key == K_ESCAPE:
            return "switch-to-mainmenu"
         else:
            if self.default_event_handler != None:
               self.default_event_handler([event])

   def update(self, screensurface):
      """ Convenient hook to plug screen updates into,
      doesn't actually do anything without being overridden,
      remember to call clock tick in your update implementation,
      pass it your screen surface for the drawatage.  Return some
      game specific logic for switching or ending or what have you."""

      self.clock_tick()

      self.curr_delay -= self.tick_time

      if self.curr_delay <= 0:
         self.curr_delay = self.flip_time

         self.credit_index += 1

         if self.credit_index >= self.credit_index_end:
            self.credit_index = 0

         self.draw = True

      #Do stuff with the screensurface here and stuff!
      if self.draw:
         screensurface.blit(self.credit_images[self.credit_index], (0,0))
         screensurface.blit(self.press_escape_surface, (5, 768 - self.press_escape_surface.get_height()))
         self.draw = False

      #Handle Input
      return self.input(pygame.event.get())
