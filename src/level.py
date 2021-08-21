# Level loading code
# Game object code may temporarily be here

import xml.parsers.expat, os, pygame, copy

class Object(pygame.sprite.Sprite):
      width = 0
      height = 0

      def __init__(self, img, x, y, width=-1, height=-1):
         super(Object, self).__init__()

         self.image = img
         self.x = x
         self.y = y

         if width == -1:
            width = img.get_width()

         if height == -1:
            height = img.get_height()

         self.width = width
         self.height = height

         self.rect = pygame.Rect(x, y, width, height)

class Tile(Object):
   gid = 0
   properties = {}

   def __init__(self, img, x, y, gid=0, properties={}):
      Object.__init__(self, img, x, y)

      # Optional
      self.gid = gid
      self.properties = copy.copy(properties)

class Level(object):
   """ Contains all information related to a level, including
       its freshly loaded state, file information, and current play information """
 
   def __init__(self, filename):
      """ Initialize and load a level object. """
      # Width in tiles
      self.width = 0

      # Height in tiles
      self.height = 0

      # Width -of- tiles
      self.tile_width = 0

      # Height -of- tiles
      self.tile_height = 0

      # Level properties
      self.properties = {}
      self.tile_properties = {}

      # Defined objects
      self.objects = []

      # Tilesets
      self.tilesets = []

      # Individual subsurfaces of the tileset keyed with gid
      self.tile_images = {}

      # Layers of tiles. 
      self.tile_layers = []
      self.rendered_tile_layers = []

      # Used as static variables for loading... don't touch
      self.loading_object = False
      
      self.loading_tileset = False
      self.tile_id = -1

      self.rect = pygame.Rect(0,0,0,0)

      ###

      self.filename = os.path.join('levels', filename + '.tmx')
      self.load()

   def load(self):
      """ Load a level file. """

      p = xml.parsers.expat.ParserCreate()
      p.StartElementHandler = self.start_element_handler
      p.EndElementHandler = self.end_element_handler

      with open(self.filename) as f:
         p.ParseFile(f)

      # Post Processing hook
      self.post_process()

   def post_process(self):
      """ Perform any additional setup for the level after it is loaded. """
      pass

   def start_element_handler(self, name, attrs):
      """ Set level data and create relevant objects. """

      if name == 'map':
         self.width = int(attrs['width'])
         self.height = int(attrs['height'])
         self.tile_width = int(attrs['tilewidth'])
         self.tile_height = int(attrs['tileheight'])

      # Add property to the most recent element's object.
      # This is relevant for the top level map and objects in object sets.
      elif name == 'property':
         if self.loading_object:
            self.objects[-1]['properties'][attrs['name']] = attrs['value']
         elif self.loading_tileset:
            self.tile_properties[self.tile_id][attrs['name']] = attrs['value']
         else:
            self.properties[attrs['name']] = attrs['value']

      elif name == 'tileset':
         attrs['tilewidth'] = int(attrs['tilewidth'])
         attrs['tileheight'] = int(attrs['tileheight'])
         attrs['firstgid'] = int(attrs['firstgid'])

         self.tilesets.append(attrs)

         self.loading_tileset = True

      # Add image to the latest tileset
      elif name == 'image':
         self.tilesets[-1]['image'] = attrs

         filename = os.path.join('sprites', attrs['source'].split('/')[-1])

         if 'trans' in attrs.keys():
            image = pygame.image.load(filename).convert()
            image.set_colorkey(pygame.Color('#' + str(attrs['trans'])))
         else:
            image = pygame.image.load(filename).convert_alpha()

         x = y = 0
         twidth = self.tilesets[-1]['tilewidth']
         theight = self.tilesets[-1]['tileheight']
         gid = self.tilesets[-1]['firstgid']

         while y < image.get_height():
            timage = image.subsurface(pygame.Rect(x,y,twidth,theight))

            self.tile_images[gid] = timage

            # Move our offsets. If we hit the side of the image, move to the next row
            x += twidth

            if x >= image.get_width():
               x = 0
               y += theight

            gid += 1

      # Add a new layer to the end
      elif name == 'layer':
         self.tile_layers.append(pygame.sprite.Group())

         # Zero out cooridinates we can use when adding tiles and
         # calculate the pixel size of the level so we know where the edges are
         self.rect = pygame.Rect(0,0, \
                                 (self.tile_width * int(attrs['width'])), \
                                 (self.tile_height * int(attrs['height'])))

      # Add tile to the latest layer
      elif name == 'tile':
         if self.loading_tileset:
            self.tile_id = int(attrs['id']) + 1
            self.tile_properties[self.tile_id] = {}
            return

         gid = int(attrs['gid'])
         
         x = self.rect.left
         y = self.rect.top

         # gid of 0 is a blank square, anything else is a tile
         if gid > 0:
            spr_props = {}

            if gid in self.tile_properties.keys():
               spr_props = self.tile_properties[gid]

            spr = Tile(self.tile_images[gid], x, y, gid, spr_props)
            self.tile_layers[-1].add(spr)

         # Move offsets
         self.rect.left += self.tile_width

         if self.rect.left >= self.rect.width:
            self.rect.left = 0
            self.rect.top += self.tile_height

      elif name == 'object':
         self.loading_object = True

         attrs['properties'] = {}
         attrs['x'] = int(attrs['x'])
         attrs['y'] = int(attrs['y'])

         if 'width' in attrs:
            attrs['width'] = int(attrs['width'])

         if 'height' in attrs:
            attrs['height'] = int(attrs['height'])

         self.objects.append(attrs)

   def end_element_handler(self, name):
      """ Pop the current element we are handling off the stack. """

      if name == 'object':
         self.loading_object = False
      elif name == 'tileset':
         self.loading_tileset = False
         self.tile_id = -1
      #elif name == 'layer':
      #   self.render_layer(-1)

   def render_layer(self, layer, rendered_layer_index = -1):
      trans_color = pygame.Color('#ff00ff')

      # Make new surface, draw the layer, and save it
      rendered_layer = pygame.Surface((self.rect.width, self.rect.height)).convert()
      rendered_layer.fill(trans_color)
      rendered_layer.set_colorkey(trans_color)

      self.tile_layers[layer].draw(rendered_layer)

      if rendered_layer_index >= 0:
         self.rendered_tile_layers[rendered_layer_index] = rendered_layer
      else:
         self.rendered_tile_layers.append(rendered_layer)

   def remove_rendered_layer(self, rendered_tile_layer_index):
      self.rendered_tile_layer.pop(rendered_tile_layer_index)
