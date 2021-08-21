import pygame, sys, os, time, math, random
from pygame.locals import *

class SoundManager():
   music_on = True
   active_song = ""
   active_loops = -1
   initialized = False
   sounds = {}

   def __init__(self):
      """ Sets up pygame mixer """

      if not self.initialized:
         pygame.mixer.pre_init(44100, -16, 2, 4096)
         pygame.mixer.init()
         
         self.initialized = True

   def toggle_music(self):
      """ Designed for use as a menu callback, turns off and restarts music.""" 

      if self.music_on == False:
         self.music_on = True
         
         if self.active_song != "":
            pygame.mixer.music.load(os.path.join("music", self.active_song))
            pygame.mixer.music.play(self.active_loops)
      else:
         self.music_on = False
         pygame.mixer.music.stop()

   def stop_music(self, fadeout=0):
      """ Stop music and reset play related variables."""
      self.active_song = ""
      self.active_loops = 0

      if fadeout > 0:
         pygame.mixer.music.fadeout(fadeout)
      else:
         pygame.mixer.music.stop()

   def load_and_play_song(self, songfile, loops = -1, volume=1.0):
      """ Loads a song and sets it to play a specified number of loops. 
      Empty string to stop music. -1 loops for indefinite playing. """
      
      if self.active_song != songfile:
         self.active_song = songfile
         self.active_loops = loops

         if self.music_on:
            pygame.mixer.music.load(os.path.join('music', self.active_song))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(self.active_loops)

   def load_sound(self, soundfile, folder='sounds'):
      """ Load a sound file, store it, and return the object. If it is already loaded, return that."""

      if soundfile in self.sounds.keys():
         return self.sounds[soundfile]
      else:
         sound = pygame.mixer.Sound(os.path.join(folder, soundfile))
         self.sounds[soundfile] = sound
         return sound

   def play_sound(self, soundfile, folder='sounds', volume=1.0, loop=0, maxtime_ms=0, fade_ms=0):
      """ Play a sound, load it if necessary. """

      sound = self.load_sound(soundfile, folder)
      sound.set_volume(volume)

      # Per the PyGame docs
      # Loop = number of -extra- times to play, so loop 5 means sound is played 6 times total
      # Maxtime = max number of ms to play the sound
      # Fade = Time to fade in from 0 volume to full volume
      return sound.play(loop, maxtime_ms, fade_ms)

   def stop_sound(self, soundfile, folder='sounds', fadeout=0):
      sound = self.load_sound(soundfile, folder)

      if fadeout > 0:
         sound.fadeout(fadeout)
      else:
         sound.stop()
