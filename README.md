# PyMaze
## About
This program provides a quick and easy solution to your maze-deficiency issues. There are generally two use cases for this program, to generate a file containing a maze to solve or to start an interactive maze game within your favorite terminal. 

# Usage
See the Details section for more details information about maze files and option details.
To create a randomly generated maze execute

	python3 maze.py

Or if on linux, the script can invoked be the default python3 interpreter

	./maze.py

By default, maze.py will generate a random 15 by 15 maze. The maze files will be created in the mazes directory. 

	./maze.py -[OPTION|ARG]*

	-width COL	Sets the maze width (number of columns) to COL, default is 15
	-height ROW	Sets the maze height (number of rows) to ROW, default is 15
	-seed SEED	Sets Random Number Generator's seed to SEED, default seed is random
	-out NAME	Sets output file prefix to NAME, default is seed number		
	-interactive	Starts CLI maze game. Does not save to file	
	-help		Prints help menu


## Examples
The following generates two files, MyMaze_maze.txt and MyMaze_portals.txt, which contain a 50x45 maze with a random seed of 13.1 

		./maze.py -width 50 -height 45 -seed 13.1 -out MyMaze

This will start an interactive 15 by 15 maze game in the terminal as demonstrated below.	

		./maze.py -interactive -width 20 -height 15 

## Interactive
![](demo.gif)



# Details
## Maze Generation
As of now, the algorithm employs a randomized [Kruskal's Algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm) to generate Mazes. 


## Maze Files
Each maze consists of two files named suffixed with _maze.txt and _portals.txt. 
The _maze.txt files is an ascii representation of the maze. 
The marks S and X within the corner cells correspond to the Start and End of the maze respectively. 
The width of the maze refers to number of columns in the maze.
The height of the maze refers to number of rows in the maze. 
By default, the name of the maze files generated will be based on the value of the seed. 
For example, if the seed used was 138.1 then the maze files will be 138.1_maze.txt and 138.1_portals.txt.


## Portals
These files are used for debugging purposes and represent the undirected edges of the maze's graph structure. 
The _portals.txt is a list of 2D coordinates. Each coordinate is a pair of cell identifiers and if a pair exists, the player may move between the two cells.

Example on a 3x3 Maze
	
	+-+-+-+
	|0 1|2|
	+ + + +
	|3|4|5|
	+ + + +
	|6|7 8|
	+-+-+-+	
Portals: (0, 1) (0, 3) (1, 4) (2, 5) (3, 6) (4, 7) (5, 8) (7, 8)

NOTICE: Portals a undirected and do not repeat, so if portal (a, b) is seen, the (b, a) will not be listed. This is to limit the number of listings since if there is a portal from (a, b), it is implied the player can move between the two cells, regardless of direction.

## Cells
Each maze is a 2D grid of cells each implicitly labeled with a unique sequential identifier. 
Cells are located at column by row coordinates. A cells coordinates are at (x, y) then its unique identifier will be equal to y*width+x. This allows to reference the cells and portals like the above 3x3 example.

## Seed Numbers
The number that is prepended to these files is the randomly generated number that seeds python's random number generator. The seed value determines the sequence of values generated, and using the same seed ontwo mazes of equal dimensions will generate the same maze. By default the seed is random if not explicitly set. So running the script without the seed option will generate a new maze each execution.


