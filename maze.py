#! /usr/bin/env python3
'''
Random Maze Generator
	Makes use of a radomized version of Kruskal's Minimum Spanning Tree (MST) 
	algorithm to generate a random ASCII maze!
@author: Paul Miller (github.com/138paulmiller)
'''



import random
import sys
import datetime as dt
import disjointSet as ds


class Maze:
	def __init__(self, width, height, seed=1):
		'''
		Default constructor to create an widthXheight maze
			width - number of columns
			height - number of rows
			seed - number to seed RNG
		'''
		assert width > 0; assert height > 0
		self.width = width
		self.height = height
		self.seed = seed
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
			for col in range(0,width)]\
				for row in range(0, height)]
		# portals[key] = {keys of neighbors}
		self.portals = {}
		# generate the maze by using a kruskals algorithm 
		self.kruskalize()	
	
	def __repr__(self):
		return self.print_maze()

	def print_maze(self):
		'''
		Defines the string representaion of the maze
		Allows for print(maze)
		'''
		s=''
		for col in range(0, self.width):
			s += '+-'
		s+='+\n'
		# wall if region not the same	
		for row in range(0,self.height):	
		# draw | if no portal between [row][col] and [row][col-1]
			if row == 0:
				s+= '|S'
			else:
				s+= '| '
			
			for col in range(1, self.width): 	
				c = '|'
				# if edge to the left
				key = self.grid[row][col]
				left_key = self.grid[row][col-1]
				#check for portal between [a][b] or [b][a]	
				if left_key in self.portals[key] or \
					key in self.portals[left_key]:
					c = ' '
				if row == self.height-1 and col == self.width-1:
					c += 'X'
				else:
					c += ' '  	
				s += c 	
			s += '|\n'
			# draw - if not portal between [row][col] and [row-1][col]
			for col in range(0, self.width):
				# if edge below (relative to view, so really above)
				c = '-'	
				key = self.grid[row][col]	
				if row+1 < self.height:
					down_key = self.grid[row+1][col]		
					if down_key in self.portals[key] or\
						key in self.portals[down_key]:
						c = ' '			
				s += '+' + c
			s+= '+\n'	
		
		return s

	def print_portals(self):
		'''
		Returns a string containing a list of all portal coordinates
		'''
		i = 1
		s = 'Portal Coordinates\n'
		for key, portals in self.portals.items():
			for near in portals.keys():
				s+= '%-015s' % (str((key, near)))
				# draw 5 portals coordinates per line
				if i % 5 == 0:
					s+='\n'
				i+=1
		return s
	
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
		'''
		# edge = ((row1, col1), (row2, col2)) such that grid[row][col] = key
		edges_ordered = [ ]
		# First add all neighboring edges into a list
		for row in range(0, self.height):
			for col in range(0, self.width):	
				cell = (row, col)
				left_cell = (row,col-1)
				down_cell = (row-1, col)
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
				key = self.grid[row][col]
				# create the singleton 
				disjoint_set.make_set(key)
				# intialize the keys portal dict
				self.portals[key] = {}
		edge_count = 0
		# eulers formula e = v-1, so the
		# minimum required edges is v for a connected graph!
		# each cell is identified by its key, and each key is a vertex on the MST
		key_count = self.grid[self.height-1][self.width-1] # last key	
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



# create throwaway function to parse argument
def parse_arg(option, argv, i, arg_type) :
		#expect integer
		try:
			return arg_type(argv[i])
		except ValueError:
			print('\nError: Invalid argument type for option: '+\
					str(option)+'\nTry \'./maze -help\' for information\n')
			sys.exit(-1) 	
		except IndexError:
			print('\nError: Missing argument for option: '+\
					str(option)+'\nTry \'./maze -help\' for information\n')
			sys.exit(-1) 	

def main():
	usage = \
	r'''
PyMaze github.com/138paulmiller
./maze -[OPTION=ARG]*
Options:
	-width COL 		COL cells for each column, default is 15
	-height ROW		ROW cells for each row, default is 15
	
	-seed INT		Sets Random Number Generator's seed to INT, default seed is random		
Example:
	To generate a 50x45 maze with a random seed of 13
	./maze -width 50 -height 45 -seed 13
	'''	
	argv = sys.argv
	argc = len(argv)
	seed = random.random()*10000		
	width = 15
	height = 15

	#parse arguments not including script path
	i = 1	
	while i < argc:
		option = argv[i]
		i+=1 # next option
		if option == '-width':
			width = parse_arg( '-width', argv, i, int)
			i+=1 # eat next arg
		elif option == '-height':
			height = parse_arg('-height', argv, i, int)
			i+=1 # eat next arg
		elif option == '-seed':
			seed = parse_arg('-seed', argv, i, float)
			i+=1 # eat next arg
		elif option == '-help':
			print(usage)
			sys.exit(-1) 		
		else:
			print("Invalid option: " + option + \
				 '\nTry \'./maze -help\' for information\n')	
			sys.exit(-1) 		
	maze = Maze(width, height, seed)

	#write the maze to a text file
	out_filename = 'mazes/%08.3f'% seed # files names based on seed used
	out_file = open(out_filename+'_maze.txt', 'w')	
	out_file.write(maze.print_maze())
	out_file.close()
	
	# write the portals to a textfile
	out_file= open(out_filename +'_portals.txt', 'w')
	out_file.write( maze.print_portals())
	out_file.close()

if __name__ == '__main__':
	main() 
