# Main file - should need very few modifications
import pygame, sys, os, time, math, random
import screen, menus, utilities

from pygame.locals import *
from gamescreen import GameScreen
from creditscreen import CreditScreen

def default_event_handler(events):
   for event in events :
      if event.type == QUIT:
         sys.exit(0)

# Set the game name
GAME_NAME = 'Cinders'

GAME_LEVELS = utilities.load_levels()

if __name__ == '__main__':
   # Initialize core and create window
   pygame.init()
   window = pygame.display.set_mode((1024, 768))
   pygame.display.set_icon(pygame.image.load(os.path.join('graphics', 'windowicon.png')).convert())
   pygame.display.set_caption(GAME_NAME)
   
   screensurface = pygame.display.get_surface()

   # Display the loading screen
   splash = pygame.image.load(os.path.join('graphics', 'splash.png')).convert()
   screensurface.blit(splash, (0,0))
   pygame.display.flip()

   # Seed prng
   random.seed()
   
   # Load art assets
   utilities.load_image('flame-up.png')
   utilities.load_image('flame-down.png')
   utilities.load_image('flame-right.png')
   utilities.load_image('flame-left.png')

   utilities.load_image('burning.png')

   utilities.load_image('cinders-down.png')
   utilities.load_image('cinders-up.png')
   utilities.load_image('cinders-right.png')
   utilities.load_image('cinders-left.png')

   title_screen_image = utilities.load_image('Cinders-title-screen.jpg', 'graphics')
   help_screen_image = utilities.load_image('Cinders-help-screen.jpg', 'graphics')
   victory_screen_image = utilities.load_image('Cinders-victory-screen.jpg', 'graphics')
   failure_screen_image = utilities.load_image('Cinders-failure-screen.jpg', 'graphics')
   wingame_screen_image = utilities.load_image('Cinders-wingame-screen.jpg', 'graphics')

   # Initialize the Game Screen
   gamescreen = GameScreen()
   gamescreen.pause_clock()
   gamescreen.default_event_handler = default_event_handler

   # Start the music
   gamescreen.sound_manager.load_and_play_song('cinder-intro.ogg',-1)
   menu_select_sound = gamescreen.sound_manager.load_sound('menu-select.wav')
   menu_select_sound.set_volume(0.2)

   # Make the credit screen
   creditscreen = CreditScreen()
   gamescreen.pause_clock()
   creditscreen.default_event_handler = default_event_handler

   # Create the menus
   start_game = menus.MenuEntry('Start Game')
   start_game.callback = lambda: "start-game"
   
   exit = menus.MenuEntry('Exit')
   exit.callback = lambda: "exit-game"

   return_to_game = menus.MenuEntry('Return to Game')
   return_to_game.callback = lambda: "switch-to-game"

   credits = menus.MenuEntry('Credits')
   credits.callback = lambda: "switch-to-credits"

   next_level = menus.MenuEntry('Next Level')
   next_level.callback = lambda: "next-level"

   retry_level = menus.MenuEntry('Retry')
   retry_level.callback = lambda: "retry-level"

   toggle_music = menus.MenuEntry('Toggle Music')
   toggle_music.callback = gamescreen.sound_manager.toggle_music
   
   restart_game = menus.MenuEntry('Play Again')
   restart_game.callback = lambda: "restart-game"
   
   gotohelp = menus.MenuEntry('Instructions')
   gotohelp.callback = lambda: "get-help"
   
   return_whence = menus.MenuEntry('Ok, Got it')
   return_whence.callback = lambda: "help-return"
   return_screen = None
   
   mainmenu = menus.MenuScreen([start_game, gotohelp, credits, toggle_music, exit], 375, "", menu_select_sound, title_screen_image)
   helpmenu = menus.MenuScreen([return_whence], 375, "", menu_select_sound, help_screen_image)
   pausemenu = menus.MenuScreen([return_to_game, gotohelp, toggle_music, exit], 375, GAME_NAME, menu_select_sound)
   victorymenu = menus.MenuScreen([next_level, exit], 375, "Victory", menu_select_sound, victory_screen_image)
   failmenu = menus.MenuScreen([retry_level, gotohelp, exit], 375, "Failure", menu_select_sound, failure_screen_image)
   wingamemenu = menus.MenuScreen([restart_game, exit], 375, "The world is ashes", menu_select_sound, wingame_screen_image)
   
   # Set our current screen
   currentscreen = mainmenu
   mainmenu.default_event_handler = default_event_handler

   screen = screen.Screen()
   screen.default_event_handler = default_event_handler
   screen.pause_clock()

   # Set the level index
   level = 0

   while True:
      status = currentscreen.update(screensurface)
      pygame.display.flip()
 
      # Check here for game-win condition because it's easier.
      if status == "switch-to-pause":
         currentscreen = pausemenu
         gamescreen.pause_clock()
      elif status == "switch-to-mainmenu":
         currentscreen = mainmenu
         creditscreen.pause_clock()
      elif status == "switch-to-credits":
         currentscreen = creditscreen
         creditscreen.unpause_clock()
      elif status == "help-return" :
         currentscreen = return_screen
      elif status == "get-help" :
         return_screen = currentscreen
         currentscreen = helpmenu
      elif status == "switch-to-game":
         currentscreen = gamescreen
         gamescreen.unpause_clock()
      elif status == "start-game" or status == "retry-level" or status == "restart-game":
         if status == "restart-game" :
            level = 0
            gamescreen.sound_manager.stop_sound('cinder-victory.wav', fadeout=500)

         gamescreen.load_level(GAME_LEVELS[level])

         gamescreen.sound_manager.stop_sound('cinder-failure.wav', fadeout=500)
         gamescreen.sound_manager.load_and_play_song('cinder-play.ogg', -1)
         
         currentscreen = gamescreen
         gamescreen.unpause_clock()
      elif status == "next-level":
         level += 1
         if GAME_LEVELS[level]:
            gamescreen.load_level(GAME_LEVELS[level])
            gamescreen.sound_manager.stop_sound('cinder-victory.wav', fadeout=500)
            gamescreen.sound_manager.load_and_play_song('cinder-play.ogg', -1)

         currentscreen = gamescreen
         gamescreen.unpause_clock()
      elif status == "level-failure":
         gamescreen.sound_manager.stop_music(fadeout=500)
         gamescreen.sound_manager.play_sound('cinder-failure.wav')

         currentscreen = failmenu
         gamescreen.pause_clock()
      elif status == "level-success":
         gamescreen.sound_manager.stop_music(fadeout=500)
         gamescreen.sound_manager.play_sound('cinder-victory.wav')
         gamescreen.pause_clock()
         if GAME_LEVELS[level+1] == None :
            currentscreen = wingamemenu
         else :
            currentscreen = victorymenu

      elif status == "exit-game":
         pygame.quit()
         sys.exit(0)
