from numpy  import *
from copy import copy
import sys, pygame, time
import os.path
import ConfigParser
from lxml import etree
pygame.init()

black = 0, 0, 0
red = 255, 0, 0

def makepainter(possibilities):
   def painter(x, y, board):
		position = board.convert_position_on_screen_to_position_on_board(x, y)
		x = position[0]
		y = position[1]
		selected = possibilities[random.randint(0,len(possibilities))]
		size = selected['size']
		x_size = size
		y_size = size
		for i in range(x, x+x_size):
			for j in range(y, y+y_size):
				if not board.is_valid_tile(i, j):
					return
		for i in range(x, x+x_size):
			for j in range(y, y+y_size):
				board.play_area[i][j] = pygame.image.load(selected['image'])
   return painter
   
class Cursor:
	def __init__(self):
		self.data = None
	def press(self, x, y, board):
		if self.data != None:
			self.data(x, y, board)

class PlayArea:
	def __init__(self, play_area_size, play_area_tile_size, usable_area, area_anchor):
		self.tiles = play_area_size #in tiles
		self.tile_size = play_area_tile_size #in pixels
		self.play_area = []
		self.usable_area = usable_area
		self.area_anchor = area_anchor
		for i in range(0, play_area_size):
			self.play_area.append([pygame.image.load("ground.png")] * self.tiles)
	def convert_position_on_screen_to_position_on_board(self, x, y):
		#may return invalid tile! Check with is_valid_tile
		x-=self.area_anchor[0]
		y-=self.area_anchor[1]
		x/=self.tile_size
		y/=self.tile_size
		return x, y
	def is_valid_tile(self, x, y):
		if x >= self.tiles:
			return False
		if y >= self.tiles:
			return False
		if x < 0 or y < 0:
			return False
		return True
	def is_free_tile(x, y):
		return self.is_valid_tile(x, y)
	def add_to_screen(self, screen):
		x_min = self.area_anchor[0]/self.tile_size
		y_min = self.area_anchor[1]/self.tile_size
		x_max = self.usable_area[0]/self.tile_size - x_min
		y_max = self.usable_area[1]/self.tile_size - y_min
		if x_max > self.tiles:
			x_max = self.tiles
		if y_max > self.tiles:
			y_max = self.tiles
		dummy = (1, 1)
		for x in range(x_min, x_max):
			for y in range(y_min, y_max):
				size = (self.tile_size, self.tile_size)
				position = (self.tile_size*(x-x_min), self.tile_size*(y-y_min))
				screen.blit(pygame.transform.scale(self.play_area[x][y], size), pygame.Rect(position, dummy))
		return screen

class Button:
	def __init__(self, function, image, position, size):
		self.size = size
		self.position = position
		self.function = function
		self.image = image
		self.surface = pygame.image.load(image)
	def press(self, x, y, cursor):
		if (self.position[0]) <= x <= (self.position[0] + self.size[0]):
			if (self.position[1]) <= y <= (self.position[1] + self.size[1]):
				cursor.data = self.function
		return cursor
	def add_to_screen(self, screen):
		dummy = (1, 1)
		screen.blit(pygame.transform.scale(self.surface, self.size), pygame.Rect(self.position, dummy))
		return screen
class Menu:
	def __init__(self, button_width, button_height, location_x_start, location_y_start):
		self.menu = []
		count = 0
		data = etree.parse('structure.xml')
		for elt in data.getiterator("buildings"):
			for e in elt:
				possibilities = []
				for sprite in e:
					possibilities.append({'image': sprite.attrib['image'], 'size': int(sprite.attrib['size'])})
				self.menu.append(Button(function=makepainter(possibilities), image=e.attrib['image'], position=(location_x_start, location_y_start+button_height*count), size=(button_width, button_height)))
				count+=1
		for elt in data.getiterator("linear"):
			for e in elt:
				possibilities = []
				for sprite in e:
					possibilities.append({'image': sprite.attrib['image'], 'size': int(sprite.attrib['size'])})
				self.menu.append(Button(function=makepainter(possibilities), image=e.attrib['image'], position=(location_x_start, location_y_start+button_height*count), size=(button_width, button_height)))
				count+=1
		for elt in data.getiterator("special"):
			for e in elt:
				possibilities = []
				for sprite in e:
					possibilities.append({'image': sprite.attrib['image'], 'size': int(sprite.attrib['size'])})
				self.menu.append(Button(function=makepainter(possibilities), image=e.attrib['image'], position=(location_x_start, location_y_start+button_height*count), size=(button_width, button_height)))
				count+=1
	def press(self, x, y, cursor):
		for thing in self.menu:
			cursor = thing.press(x, y, cursor)
	def add_to_screen(self, screen):
		for thing in self.menu:
			screen = thing.add_to_screen(screen)
		return screen

class Game:
	def __init__(self):
		default_settings = [[{
			'screen_width': 900,
			'screen_height': 710,
			'button_width': 80,
			'button_height': 80,
			'play_area_tile_size': 25,
			}, 'display'], [{
			'play_area_size': 100,
			}, 'play_area']]
		settings = self.load_settings_from_file(default_settings)
		size = settings['screen_width'], settings['screen_height']
		self.screen_width = settings['screen_width']
		self.screen_height = settings['screen_height']
		self.button_width = settings['button_width']
		self.button_height = settings['button_height']
		self.screen = pygame.display.set_mode(size)
		self.board = PlayArea(settings['play_area_size'], settings['play_area_tile_size'], (settings['screen_width']-self.button_width, self.screen_height), (0, 0))
		self.menu = Menu(settings['button_width'], self.button_height, location_x_start=settings['screen_width']-self.button_width, location_y_start=0)
		self.cursor = Cursor()
	def press(self, event):
		# Set the x, y positions of the mouse click
		x, y = event.pos
		self.menu.press(x, y, self.cursor)
		self.cursor.press(x, y, self.board)
	
	def update_screen(self):
		self.screen.fill(black)
		dummy = (1, 1)
		self.screen = self.menu.add_to_screen(self.screen)
		self.screen = self.board.add_to_screen(self.screen)
		pygame.display.flip()

	def get_settings_filename(self):
		return "settings.cfg"

	def load_settings_from_file(self, default_settings):
		loaded_settings = {}
		unified_defaults = {}
		for set in default_settings:
			unified_defaults = dict(unified_defaults, **set[0])
		config = ConfigParser.SafeConfigParser()
		config.read(self.get_settings_filename())
		for set in default_settings:
			section = set[1]
			for name in set[0]:
				try:
					loaded_settings[name] = config.getint(section, name)
				except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
					loaded_settings[name] = unified_defaults[name]
		return loaded_settings
	def save_settings_to_file(self):
		config = ConfigParser.RawConfigParser()
		# When adding sections or items, add them in the reverse order of
		# how you want them to be displayed in the actual file.
		# In addition, please note that using RawConfigParser's and the raw
		# mode of ConfigParser's respective set functions, you can assign
		# non-string values to keys internally, but will receive an error
		# when attempting to write to a file or when you get it in non-raw
		# mode. SafeConfigParser does not allow such assignments to take place.
		config.add_section('display')
		config.set('display', 'screen_width', str(self.screen_width))
		config.set('display', 'screen_height', str(self.screen_height))
		config.set('display', 'button_width', str(self.button_width))
		config.set('display', 'button_height', str(self.button_height))
		config.set('display', 'play_area_tile_size', str(self.board.tile_size))
		config.add_section('play_area')
		config.set('play_area', 'play_area_size', str(self.board.tiles))
		# Writing our configuration file
		with open(self.get_settings_filename(), 'wb') as configfile:
			config.write(configfile)	

def init():
	global blob
	blob = Game()
	blob.save_settings_to_file()

def main_loop():
	#print pygame.mouse.get_rel()
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				blob.press(event)
		blob.update_screen()

init()
main_loop()