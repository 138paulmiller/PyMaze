#! /usr/bin/env python3
'''
Random Maze Generator
Makes use of a radomized version of Kruskal's Minimum Spanning Tree (MST) 
algorithm to generate a random ASCII maze!
@author: Paul Miller (github.com/138paulmiller)
'''

import os, sys, tty, random
# defined in disjointSet.py
import disjointSet as ds

class Maze:
	# static variables
	# Directions to move the player. 
	# Note, up and down are reversed (visual up and down not grid coordinates)	
	UP = (0, -1)
	DOWN = (0, 1)
	LEFT = (-1, 0)
	RIGHT = (1,0)
	# defalt ANSI settings from user
	COLOR_DEFAULT = u'\u001b[0m'
	# foreground colors (text)
	COLOR_BLACK = u'\u001b[30m'
	COLOR_RED =  u'\u001b[31m'
	COLOR_GREEN = u'\u001b[32m'
	COLOR_YELLOW = u'\u001b[33m'
	COLOR_BLUE  =u'\u001b[34m'
	COLOR_MAGENTA = u'\u001b[35m'
	COLOR_CYAN = u'\u001b[36m'
	COLOR_WHITE = u'\u001b[37m'
	# background colors 
	COLOR_BG_BLACK = u'\u001b[40m'
	COLOR_BG_RED =  u'\u001b[41m'
	COLOR_BG_GREEN =  u'\u001b[42m'
	COLOR_BG_YELLOW = u'\u001b[43m'
	COLOR_BG_BLUE = u'\u001b[44m'
	COLOR_BG_MAGENTA =  u'\u001b[45m'
	COLOR_BG_CYAN = u'\u001b[46m'
	COLOR_BG_WHITE= u'\u001b[47m'

	def __init__(self, width, height, seed, symbols):
		'''
		Default constructor to create an widthXheight maze
		@params 
			width(int)	: number of columns
			height(int)	: number of rows
			seed(float)	: number to seed RNG
			symbols(dict)	: used to modify maze symbols and colors
							settings{
								start, end, start_color, end_color, : start and end symbols and colors
								wall_v, wall_h, wall_c, wall_color, : vertical,horizontal and corner wall symbols and colors 
								head, tail, head_color, tail_color   : player head and trail symbols and colors
								*_bg_color, : substitute _color with bg_color to set background colors 
		@return												
			Maze	: constructed object
		'''
		assert width > 0; assert height > 0
		self.width = width
		self.height = height
		self.seed = seed
		self.init_symbols(symbols)
		self.path_map  = {} # quick lookup for paths and player
		self.path = [] # current path taken
		self.player = (0,0) # players position
		# self.items = [(x,y)] #TODO?? Add a list of possible items to collect for points?
        # Creates 2-D array of cells(unique keys)
		# Grid is 2-D, and the unique ids are sequential, i
		# so uses a 2-D to 1-D mapping
		# to get the key since row+col is not unique for all rows and columns
		#	E.g.
		#	width = 5
		#			1-D Mapping	vs  	Naive
		#	grid[2][3] = 	5*2+3 = 13 	vs  	2+3 = 6
		#	grid[3][2] =	5*3+2 = 17	vs 	3+2 = 6 X Not unique! 
		# use 2D list comprehensions to avoid iterating twice
		self.grid = [[(width*row + col) \
			for row in range(0,height)]\
				for col in range(0, width)]
		# portals[key] = {keys of neighbors}
		self.portals = {}
		# generate the maze by using a kruskals algorithm 
		self.kruskalize()	
	

	def __repr__(self):
		'''
		Allows for print(maze)
		@params
			None
		@return
			String : Ascii representation of the Maze
		'''
		return self.to_str()

	def to_str(self):
		'''
		Defines the string representaion of the maze
		@return
			Maze	: constructed object
		'''	
		s=''
		for col in range(0, self.width):
			s+=self.wall_c + self.wall_h
		
		s+=self.wall_c+'\n'
		# wall if region not the same	
		for row in range(0,self.height):	
			# draw S for start if at (0,0)
			if row == 0:
				s+=self.wall_v + self.start
			else:
				s+=self.wall_v
				# else draw o for vertical moves in path
				if (0, row) in self.path:
					s+=self.tail
				# or # to denote player pos
				elif (0, row) == self.player:
					s+=self.head
				# or empty
				else:
					s+=self.empty	
			# draw | if no portal between [row][col] and [row][col-1]	
			for col in range(1, self.width): 	
				# if edge to the left
				key = self.grid[col][row]
				left_key = self.grid[col-1][row]
				#initially draw wall				
				c = self.wall_v
				#check for portal between [a][b] or [b][a]	
				if left_key in self.portals[key] or \
					key in self.portals[left_key]:
						# if portal remove wall
						# if portal is inbetween paths, color  as tail
						if ((col, row) in self.path_map and (col-1, row) in self.path_map) or\
							((col-1, row) in self.path_map and (col, row) == self.player) or\
							((col, row) in self.path_map and (col-1, row) == self.player)   :
							c = self.tail
						else:
							c = self.empty
				# if at [width-1][height-1] draw end marker
				if row == self.height-1 and col == self.width-1:
					c += self.end	
				else: # draw path or player marker if if
					# any in path draw o for horizontal moves in path
					if (col, row) in self.path:	
						c+=self.tail
					# or # to denote player pos
					elif (col,row) == self.player:
						c+=self.head
					else:
						c += self.empty
				s += c 	
			s+=self.wall_v +'\n'

			# draw - if not portal between [row][col] and [row-1][col]
			for col in range(0, self.width):
				# if edge below (relative to view, so really above)
				c =self.wall_h

				key = self.grid[col][row]	
				if row+1 < self.height:
					down_key = self.grid[col][row+1]		
					if down_key in self.portals[key] or\
						key in self.portals[down_key]:
						# if portal is inbetween paths, color  as tail
						if ((col, row) in self.path_map and (col, row+1) in self.path_map) or\
							((col, row+1) in self.path_map and (col, row) == self.player) or\
							((col, row) in self.path_map and (col, row+1) == self.player)   :
							c = self.tail
						else:
							c = self.empty			
				s+=self.wall_c + c
			s+=self.wall_c +'\n'
		s+=self.empty
		return s

	def portals_str(self):
		'''
		Returns a string containing a list of all portal coordinates
		'''
		i = 1
		s = 'Portal Coordinates\n'
		for key, portals in self.portals.items():
			for near in portals.keys():
		                        # print the cell ids
				s += '%-015s' % (str((key, near)))
				# draw 5 portals coordinates per line
				if i % 5 == 0:
					s+='\n'
				i+=1
		return s

	def init_symbols(self, symbols):
		# if custom symbols
		if symbols:
			#get symbol colors _color + bg_color
			start_color = symbols['start_color'] if 'start_color' in symbols else ''
			start_bg_color = symbols['start_bg_color'] if 'start_bg_color' in symbols else ''

			end_color = symbols['end_color'] if 'end_color' in symbols else ''
			end_bg_color = symbols['end_bg_color'] if 'end_bg_color' in symbols else ''

			wall_color = symbols['wall_color'] if 'wall_color' in symbols else ''
			wall_bg_color=symbols['wall_bg_color'] if 'wall_bg_color' in symbols else''
			
			head_color = symbols['head_color'] if 'head_color' in symbols else ''
			head_bg_color=symbols['head_bg_color'] if 'head_bg_color' in symbols else ''

			tail_color = symbols['tail_color'] if 'tail_color' in symbols else self.COLOR_DEFAULT
			tail_bg_color = symbols['tail_bg_color'] if 'tail_bg_color' in symbols else self.COLOR_DEFAULT

		
			# symbol colors
			self.start = start_bg_color	+ start_color 	+ symbols['start']
			self.end =  end_bg_color 	+ end_color 	+ symbols['end']    
			self.wall_h = wall_bg_color	+ wall_color 	+ symbols['wall_h'] 
			self.wall_v = wall_bg_color	+ wall_color 	+ symbols['wall_v'] 
			self.wall_c = wall_bg_color	+ wall_color 	+ symbols['wall_c'] 
			self.head = head_bg_color 	+ head_color 	+ symbols['head']   
			self.tail = tail_bg_color 	+ tail_color 	+ symbols['tail']   
			self.empty = self.COLOR_DEFAULT+' '
		else:
			# default symbols
			self.start = 'S'
			self.end = 'X'
			self.wall_v  = '|'
			self.wall_h = '-'
			self.wall_c = '+'
			self.head =  '#'
			self.tail = 'o'	
			self.empty = ' '	

	def kruskalize(self):
		'''
		Kruskal's algorithm, except when grabbing the next available edge, 
		order is randomized. 
		Uses a disjoint set to create a set of keys. 
		Then for each edge seen, the key for each cell is used to determine 
		whether or not the the keys are in the same set.
		If they are not, then the two sets each key belongs to are unioned.
		Each set represents a region on the maze, this finishes until all
		keys are reachable (MST definition) or rather all keys are unioned into 
		single set. 
		@params
			None 
		@return
			None
		'''
		# edge = ((row1, col1), (row2, col2)) such that grid[row][col] = key
		edges_ordered = [ ]
		# First add all neighboring edges into a list
		for row in range(0, self.height):
			for col in range(0, self.width):	
				cell = (col, row)
				left_cell = (col-1, row)
				down_cell = (col, row-1)
				near = []
				# if not a boundary cell, add edge, else ignore
				if col > 0:
					near.append((left_cell, cell))
				if row > 0:
					near.append( (down_cell, cell))
				edges_ordered.extend(near)
				
		# seed the random value
		random.seed(self.seed)
		edges = []
		# shuffle the ordered edges randomly into a new list 
		while len(edges_ordered) > 0:
			# randomly pop an edge
			edges.append(edges_ordered.pop(random.randint(0,len(edges_ordered))-1))
		disjoint_set = ds.DisjointSet()
		for row in range(0, self.height):
			for col  in range(0,self.width):
				# the key is the cells unique id
				key = self.grid[col][row]
				# create the singleton 
				disjoint_set.make_set(key)
				# intialize the keys portal dict
				self.portals[key] = {}
		edge_count = 0
		# eulers formula e = v-1, so the
		# minimum required edges is v for a connected graph!
		# each cell is identified by its key, and each key is a vertex on the MST
		key_count = self.grid[self.width-1][self.height-1] # last key	
		while edge_count < key_count:
			# get next edge ((row1, col1), (row2,col2))
			edge = edges.pop()
			# get the sets for each vertex in the edge
			key_a = self.grid[edge[0][0]][edge[0][1]]
			key_b = self.grid[edge[1][0]][edge[1][1]]
			set_a = disjoint_set.find(key_a)
			set_b = disjoint_set.find(key_b)
			# if they are not in the same set they are not in the 
			# same region in the maze
			if set_a != set_b:
				# add the portal between the cells, 
				# graph is undirected and will search
				# [a][b] or [b][a]
				edge_count+=1	
				self.portals[key_a][key_b] = True 
				disjoint_set.union(set_a, set_b)

	def move(self, direction):
		'''
		Used to indicate of the player has completed the maze
		@params
			direction((int, int)) : Direction to move player
									  
		@return
			None
		'''
		assert(direction in [self.LEFT, self.RIGHT, self.UP, self.DOWN])
		# if new move is the same as last move pop from path onto player 
		new_move = (self.player[0]+direction[0],\
					self.player[1]+direction[1]) 
		# if new move is not within grid
		if new_move[0] < 0 or new_move[0] >= self.width or\
			new_move[1] < 0 or new_move[1] >= self.height:
			return 
		#if theres a portal between player and newmove
		player_key = self.width*self.player[1] + self.player[0]		
		move_key = self.width*new_move[1] + new_move[0]	
		
		if move_key in self.portals[player_key] or\
			player_key in self.portals[move_key]: 
			if len(self.path) > 0 and new_move == self.path[-1]:
				self.player = self.path.pop()
				self.path_map.pop(self.player, None)
			else:
				self.path.append(self.player)
				self.path_map[self.player] = True
				self.player = new_move
	
	
	def is_done(self):
		'''
		Used to indicate of the player has completed the maze
		@params
			None 
		@return
			True if player has reached the end
		'''
		return self.player == (self.width-1, self.height-1)

	
def getchar():
	# Determine which getchar method to use
	if os.name!='nt':
		# import unix terminal interface
		import termios
		# get stdin file descriptor 
		file_desc = sys.stdin.fileno()
		# get stdin file settings
		settings = termios.tcgetattr(file_desc)
		try:
			# set tty to read raw input (unbuffered)
			# modifies settings
			tty.setraw(file_desc)
			# read a single byte 
			char = sys.stdin.read(1)
		finally:
			# set the stdin settings back to before raw modification
			termios.tcsetattr(file_desc, termios.TCSADRAIN, settings)
	# use windows getchar
	else:
		import msvcrt
		char = msvcrt.getch
	return char

def save_maze(maze, out_filename):        
	#write the maze to a text file
	out_file = open(out_filename+'_maze.txt', 'w')	
	out_file.write(maze.to_str())
	out_file.close()

	# write the portals to a textfile
	out_file= open(out_filename +'_portals.txt', 'w')
	out_file.write( maze.portals_str())
	out_file.close()


	
def play_maze(maze):
	move = 0
	quit_key = ord('q')
	up_key = lambda key: key == ord('w') or key == ord('A')
	down_key = lambda key: key == ord('s') or key == ord('B')
	right_key = lambda key: key == ord('d') or key == ord('C')
	left_key = lambda key: key == ord('a') or  key == ord('D')

	#clear the screen clear if linux, cls if windows
	os.system('clear' if os.name!='nt' else 'cls')	
	print(r'''
		PyMaze 
	Make it to the X!

Controls:
	Use the Arrow Keys or W A S D  to navigate
	q To give up

Press any key to start!
	''')
	getchar()
	os.system('clear' if os.name!='nt' else 'cls')	
	print(maze)

	# exit when either ESC or q are entered
	while move != quit_key and not maze.is_done():
	# get the integer value of character input 
		move = ord(getchar())
		# update maze based on input
		if up_key(move):
			maze.move(Maze.UP)
		elif down_key(move):
			maze.move(Maze.DOWN)
		elif right_key(move):
			maze.move(Maze.RIGHT)
		elif left_key(move):
			maze.move(Maze.LEFT)	
		os.system('clear' if os.name!='nt' else 'cls')
		print(maze)

	# say goodbye
	print('Thanks for Playing!');
		

def error(msg):
	print(msg+'\nTry \'./maze -help\' for information\n')
	sys.exit(-1) 

# move throwaway function to parse argument
def parse_arg(option, argv, i, arg_type) :
    #expect integer
	try:
		return arg_type(argv[i])
	except ValueError:
		error('\nError: Invalid argument type for option: '+ str(option))
	except IndexError:
		error('\nError: Missing argument for option: '+str(option))


def main():
	usage = \
	r'''
PyMaze github.com/138paulmiller
	./maze.py -[OPTION=ARG]*
Options:
	-width COL	Sets the maze width (number of columns) to COL (Must be greater than 0). default is 15
	-height ROW	Sets the maze height (number of rows) to ROW (Must be greater than 0). Default is 15
	-seed SEED	Sets Random Number Generator's seed to SEED.  Default seed is random
	-out NAME	Sets output file prefix to NAME, default is seed number		
	-interactive	Starts CLI maze game. Does not save to file	
	-block	Print maze using Unicode block characters and ANSI style coloring, only works with interactive mode	
	-help	Prints this menu
Example:
	The following generates two files, MyMaze_maze.txt and MyMaze_portals.txt, which contain a 50x45 maze with a random seed of 13.1 
		./maze.pys -width 50 -height 45 -seed 13.1 -out MyMaze
	This will start the interactive maze in the terminal 	
		./maze.py -interactive	
	'''	
	argv = sys.argv
	argc = len(argv)

	# set option defaults
	seed = random.random()*10000		
	width = 15
	height = 15 
	interactive = False

	block_symbols = {
		'start' : u'O',
		'end' : u'X',
		'wall_v' : u'█',
		'wall_h' : u'█',
		'wall_c' : u'█',
		'head' : u'█',
		'tail' : u'█',
		'wall_color' : Maze.COLOR_BLUE,
		'head_color' : Maze.COLOR_RED,
		'tail_color' : Maze.COLOR_CYAN,
		'start_bg_color' : Maze.COLOR_BG_YELLOW,
		'end_bg_color' : Maze.COLOR_BG_YELLOW
	}
	symbols = None
	out_filename_default = 'mazes/%08.3f'% seed
	out_filename = out_filename_default # default file names is in mazes dir and seed used
	#parse arguments not including script path
	i = 1	
	while i < argc:
		option = argv[i]
		i+=1 # next option
		if option == '-width':
			width = parse_arg( '-width', argv, i, int)
			if width <= 0:
				error('Invalid argument: width must be a positive integer')

			i+=1 # eat next arg
		elif option == '-height':
			height = parse_arg('-height', argv, i, int)
			if height <= 0:
				error('Invalid argument: width must be a positive integer')
			i+=1 # eat next arg
		elif option == '-seed':
			seed = parse_arg('-seed', argv, i, float)
			# reevaluate name
			out_filename = 'mazes/%08.3f'% seed 
			i+=1 # eat next arg
		elif option == '-out':
			out_filename = parse_arg('-out', argv, i, str)
			i+=1 # eat next arg
		elif option == '-interactive':
			interactive = True
		elif option == '-block':
			symbols = block_symbols
		elif option == '-help':
			print(usage)
			sys.exit(-1) 		
		else:
			error('Invalid option: ' + option )	
			
	#create the maze
	maze = Maze(width, height, seed, symbols)
	# activate a repl-like command interpreter to try to solve the maze 
	if interactive:
		if out_filename_default != out_filename:		
			error('Error: Output file NOT compatible with interactive mode')	
		else:
			play_maze(maze)
	else:
		# if using block symbols and printing to file print error
		if symbols:		
			error('Error: Block mode only compatible with interactive mode')	
		else:
			save_maze(maze, out_filename)
			
if __name__ == '__main__':
	main() 
