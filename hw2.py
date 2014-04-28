from sudoku import *
import math,random,copy

class Constraint():
	def __init__(self,legalVals,isAssigned):
		self.legalVals = legalVals
		self.isAssigned= isAssigned

class ConstraintBoard():
	def __init__(self,size,constraints):
		self.BoardSize=size
		self.Constraints = constraints
		self.changes =[]

	def updateConstraints(self,row,col,val):
		self.Constraints[row][col].isAssigned = True
		subsquare = int(math.sqrt(self.BoardSize))
		#update the row
		for i in range(self.BoardSize):
			if len(self.Constraints[row][i].legalVals):
				if val in self.Constraints[row][i].legalVals:
					self.changes.append(((row,i),self.Constraints[row][i].legalVals)
					self.Constraints[row][i].legalVals.remove(val)
		#update the col
		for j in range(self.BoardSize):
			if j!=row:
				if len(self.Constraints[j][col].legalVals):
					if val in self.Constraints[j][col].legalVals:
						self.changes.append(((j,col),self.Constraints[j][col].legalVals))
						self.Constraints[j][col].legalVals.remove(val)
		#update the subsquare
		squareRow = row // subsquare
		squareCol = col // subsquare
		for i in range(subsquare):
			for j in range(subsquare):
				x = squareRow*subsquare+i
				y = squareCol*subsquare+j
				if x!=row and y != col:
					if len(self.Constraints[x][y].legalVals):
						try:
							self.Constraints[x][y].legalVals.remove(val)
						except:
							pass
		return ConstraintBoard(self.BoardSize,self.Constraints)
	'''
	def undo(self,row,col,val):
		self.Constraints[row][col].isAssigned=False
		subsquare = int(math.sqrt(self.BoardSize))

		for i in range(self.BoardSize):
			if i!=col:
				self.Constraints[row][i].legalVals.append(val)
		for j in range(self.BoardSize):
			if j!=row:
				self.Constraints[j][col].legalVals.append(val)
		squareRow = row // subsquare
		squareCol = row //subsquare
		for i in range(subsquare):
			for j in range(subsquare):
				x = squareRow*subsquare+i
				y = squareCol*subsquare+j
				if x == row:
					pass
				elif y == col:
					pass
				elif x == row and y ==col:
					pass
				else:
					self.Constraints[x][y].legalVals.append(val)
		self.Constraints[row][col].legalVals.append(val)
		return ConstraintBoard(self.BoardSize,self.Constraints)
	'''

def forwardCheck(cb):#return false if no legalValues for a cell else true
	size = cb.BoardSize
	for i in range(size):
		for j in range(size):
			if cb.Constraints[i][j].isAssigned==False and len(cb.Constraints[i][j].legalVals)==0:
				return False
	return True

def getEmptySquareRandomly(sb):
	for i in range(sb.BoardSize):
		for j in range(sb.BoardSize):
			if sb.CurrentGameboard[i][j]==0:
				return (i,j)

#######
#I'm working on the Minimum remaining value with minimum constraining 
'''
def minimumRemainingValue(cb):##return the minimum remaining values
	size = cb.BoardSize
	minimum = float("inf")
	for i in range(size):
		for j in range(size):
			if(not cb.Constraints[i][j].isAssigned):
				remainingVals = len(cb.Constraints[i][j].legalVals)
				if(minimum>remainingVals):
					minimum = remainingVals
	return minimum

def getEmptySquareMRVAndMCV(cb):
	minimum = minimumRemainingValue(cb)

	sameMRV = []
	MCV =[]
	size = cb.BoardSize
	for i in range(size):
		for j in range(size):
			if(not cb.Constraints[i][j].isAssigned):
				if(minimum == len(cb.Constraints[i][j].legalVals)):
					sameMRV.append((i,j))

	for loc in sameMRV:
		mvc =0
		row = loc[0]
		col = loc[1]
		for i in range(size):
#########
'''
def backtracking(Sudokuboard,SudokuConstraintBoard):
	if iscomplete(Sudokuboard.CurrentGameboard):
		for i in range(Sudokuboard.BoardSize): 
			print Sudokuboard.CurrentGameboard[i]
		#print variable_assign
		return True
	else:
		(row,col) = getEmptySquareRandomly(Sudokuboard)
		#(row,col) = getEmptySquareMRV(SudokuConstraintBoard)
		legalVals = SudokuConstraintBoard.Constraints[row][col].legalVals
		for v in legalVals:
			#myCopyOfSBoard = copy.deepcopy(Sudokuboard)
			#myCopyOfSBoard = myCopyOfSBoard.set_value(row,col,v)
			#variable_assign +=1
			#myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
			#myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,v)
			Sudokuboard = Sudokuboard.set_value(row,col,v)
			SudokuConstraintBoard= SudokuConstraintBoard.updateConstraints(row,col,v)
			if forwardCheck(SudokuConstraintBoard)==True:
				if backtracking(Sudokuboard,SudokuConstraintBoard)==True:
					return True
			Sudokuboard = Sudokuboard.set_value(row,col,0)
			SudokuConstraintBoard = SudokuConstraintBoard.undo(row,col,v)
	return False

def test(Sudokuboard,SudokuConstraintBoard):
	print "Initial State"
	for x in range(9):
		print SudokuConstraintBoard.Constraints[0][x].legalVals
	for y in range(9):
		print SudokuConstraintBoard.Constraints[y][0].legalVals
	print "\n"
	print "Changed State"
	SudokuConstraintBoard = SudokuConstraintBoard.updateConstraints(0,0,1)
	for x in range(9):
		print SudokuConstraintBoard.Constraints[0][x].legalVals
	for y in range(9):
		print SudokuConstraintBoard.Constraints[y][0].legalVals
	print "\n"
	print "Back to Initial State"
	SudokuConstraintBoard= SudokuConstraintBoard.undo(0,0,1)
	for x in range(9):
		print SudokuConstraintBoard.Constraints[0][x].legalVals
	for y in range(9):
		print SudokuConstraintBoard.Constraints[y][0].legalVals

def main():
	#initialize environment
	file_name= '9by9Test.txt'
	sb = init_board(file_name)
	size = sb.BoardSize
	constraints = [[Constraint([1,2,3,4,5,6,7,8,9],False) for i in range(size)] for x in range(size)]
	cb = ConstraintBoard(size,constraints)
	for i in range(size):
		for j in range(size):
			if sb.CurrentGameboard[i][j]!=0:
				cb.updateConstraints(i,j,sb.CurrentGameboard[i][j])
	test(sb,cb)
	'''
	print 'Initial:'
	for i in range(size):
		print sb.CurrentGameboard[i]

	print '\n Completed:'
	x = backtracking(sb,cb)
	'''


main()

#forward checking if any of the legalValues becomes null and isn't assigned a value then we have a problem
# so that is when it should skip testing for backtracking
