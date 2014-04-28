from sudoku import *
import math,random,copy,time

####Helper classes
class Constraint():
	def __init__(self,legalVals,isAssigned):
		self.legalVals = legalVals
		self.isAssigned= isAssigned

class ConstraintBoard():
	def __init__(self,size,constraints): # ,changes=[]):
		self.BoardSize=size
		self.Constraints = constraints
		#self.changes =changes

	def updateConstraints(self,row,col,val):
		self.Constraints[row][col].isAssigned = True
		self.Constraints[row][col].legalVals.remove(val)
		subsquare = int(math.sqrt(self.BoardSize))
		#self.changes=[]
		#update the row
		for i in range(self.BoardSize):
			if i!=col:
				if len(self.Constraints[row][i].legalVals):
					if val in self.Constraints[row][i].legalVals:
						#self.changes.append(((row,i),copy.copy(self.Constraints[row][i].legalVals)))
						self.Constraints[row][i].legalVals.remove(val)
		#update the col
		for j in range(self.BoardSize):
			if j!=row:
				if len(self.Constraints[j][col].legalVals):
					if val in self.Constraints[j][col].legalVals:
						#self.changes.append(((j,col),copy.copy(self.Constraints[j][col].legalVals)))
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
						if val in self.Constraints[x][y].legalVals:
							#self.changes.append(((x,y),copy.copy(self.Constraints[x][y].legalVals)))
							self.Constraints[x][y].legalVals.remove(val)
		return ConstraintBoard(self.BoardSize,self.Constraints)
	'''
	def undo(self,row,col,val):
		self.Constraints[row][col].isAssigned=False
		self.Constraints[row][col].legalVals.append(val)

		for v in self.changes:
			row = v[0][0]
			col = v[0][1]
			self.Constraints[row][col].legalVals = v[1]
		return ConstraintBoard(self.BoardSize,self.Constraints)
	'''
##########
##########
#CSP Related Functions
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

def minimumRemainingValue(cb):##return the minimum remaining values
	size = cb.BoardSize
	minimum = float("inf")
	for i in range(size):
		for j in range(size):
			if not cb.Constraints[i][j].isAssigned:
				remainingVals = len(cb.Constraints[i][j].legalVals)
				if minimum>remainingVals:
					minimum = remainingVals
	return minimum
#MRV = minimum remaining values
#MCV = most constraining Variable
def getEmptySquareMRVAndMCV(cb):
	minimum = minimumRemainingValue(cb)
	sameMRV = []
	size = cb.BoardSize
	for i in range(size):
		for j in range(size):
			if not cb.Constraints[i][j].isAssigned:
				if(minimum == len(cb.Constraints[i][j].legalVals)):
					sameMRV.append((i,j))

	(optRow,optCol) = (sameMRV[0][0],sameMRV[0][1])
	if len(sameMRV)>1:
		maxMCV = float("-inf")
		subsquare = int(math.sqrt(size))
		for loc in sameMRV:
			mcv = 0
			row = loc[0]
			col = loc[1]
			for i in range(size):#row search
				if i!=col:
					if cb.Constraints[row][i].isAssigned==False: 
						mcv +=1
			for j in range(size):#col search
				if j!=row:
					if cb.Constraints[j][col].isAssigned==False:
						mcv+=1
			squareRow = row // subsquare
			squareCol = col // subsquare
			for i in range(subsquare):#subsquare search
				for j in range(subsquare):
					x = squareRow*subsquare+i
					y = squareCol*subsquare+j
					if x!= row and y!=col:
						if cb.Constraints[x][y].isAssigned==False:
							mcv+=1
			if mcv>maxMCV:
				maxMCV=mcv
				(optRow,optCol) = (row,col)
	return (optRow,optCol)

def leastConstrainingValue(row,col,cb):
	legalVals = cb.Constraints[row][col].legalVals
	size = cb.BoardSize
	subsquare = int(math.sqrt(size))
	lcv = 0
	minLCV = float("inf")
	for val in legalVals:
		tempLCV=0
		for i in range(size):
			if i!=col:
				if cb.Constraints[row][i].isAssigned==False and  val in cb.Constraints[row][i].legalVals:
					tempLCV+=len(cb.Constraints[row][i].legalVals)-1
		for j in range(size):
			if j!=row:
				if cb.Constraints[j][col].isAssigned==False and  val in cb.Constraints[j][col].legalVals:
					tempLCV+=len(cb.Constraints[row][i].legalVals)-1
		squareRow = row // subsquare
		squareCol = col // subsquare
		for i in range(subsquare):
			for j in range(subsquare):
				x = squareRow*subsquare+i
				y = squareCol*subsquare+j
				if x!= row and y!=col:
					if cb.Constraints[x][y].isAssigned==False and val in cb.Constraints[x][y].legalVals:
						tempLCV+=len(cb.Constraints[row][i].legalVals)-1
		if tempLCV<minLCV:
			lcv=val
			minLCV=tempLCV
	return lcv

############
##########
#Different Backtracking functions
def backTrackingWithMRVandMCVandLCV(Sudokuboard,SudokuConstraintBoard,variable_assign):
	if iscomplete(Sudokuboard.CurrentGameboard):
		for i in range(Sudokuboard.BoardSize): 
			print Sudokuboard.CurrentGameboard[i]
		print variable_assign
		return True
	else:
		(row,col) = getEmptySquareMRVAndMCV(SudokuConstraintBoard)
		print row, col
		legalVals = SudokuConstraintBoard.Constraints[row][col].legalVals
		print legalVals
		lcv = leastConstrainingValue(row,col,SudokuConstraintBoard)
		print lcv
		variable_assign +=1
		Sudokuboard = Sudokuboard.set_value(row,col,lcv)
		myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
		myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,lcv)
		if forwardCheck(myCopyOfCBoard)==True:
			if backTrackingWithMRVandMCVandLCV(Sudokuboard,myCopyOfCBoard,variable_assign)==True:
				return True
		Sudokuboard = Sudokuboard.set_value(row,col,0)
	return False	

def backTrackingWithMRVandMCV(Sudokuboard,SudokuConstraintBoard,variable_assign):
	if iscomplete(Sudokuboard.CurrentGameboard):
		for i in range(Sudokuboard.BoardSize): 
			print Sudokuboard.CurrentGameboard[i]
		print variable_assign
		return True
	else:
		(row,col) = getEmptySquareMRVAndMCV(SudokuConstraintBoard)### here
		legalVals = SudokuConstraintBoard.Constraints[row][col].legalVals
		for v in legalVals:
			variable_assign +=1
			Sudokuboard = Sudokuboard.set_value(row,col,v)
			myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
			myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,v)
			if forwardCheck(myCopyOfCBoard)==True:
				if backTrackingWithMRVandMCV(Sudokuboard,myCopyOfCBoard,variable_assign)==True:
					return True
			Sudokuboard = Sudokuboard.set_value(row,col,0)
	return False

def backTrackingWithFC(Sudokuboard,SudokuConstraintBoard,variable_assign):
	if iscomplete(Sudokuboard.CurrentGameboard):
		for i in range(Sudokuboard.BoardSize): 
			print Sudokuboard.CurrentGameboard[i]
		print variable_assign
		return True
	else:
		(row,col) = getEmptySquareRandomly(Sudokuboard)
		legalVals = SudokuConstraintBoard.Constraints[row][col].legalVals
		for v in legalVals:
			variable_assign +=1
			Sudokuboard = Sudokuboard.set_value(row,col,v)
			myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
			myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,v)
			if forwardCheck(myCopyOfCBoard)==True:						###HERE
				if backTrackingWithFC(Sudokuboard,myCopyOfCBoard,variable_assign)==True:
					return True
			Sudokuboard = Sudokuboard.set_value(row,col,0)
	return False

def simpleBackTracking(Sudokuboard,SudokuConstraintBoard,variable_assign):
	if iscomplete(Sudokuboard.CurrentGameboard):
		for i in range(Sudokuboard.BoardSize): 
			print Sudokuboard.CurrentGameboard[i]
		print variable_assign
		return True
	else:
		(row,col) = getEmptySquareRandomly(Sudokuboard)
		legalVals = SudokuConstraintBoard.Constraints[row][col].legalVals
		for v in legalVals:
			variable_assign +=1
			Sudokuboard = Sudokuboard.set_value(row,col,v)
			myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
			myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,v)
			if simpleBackTracking(Sudokuboard,myCopyOfCBoard,variable_assign)==True:
				return True
			Sudokuboard = Sudokuboard.set_value(row,col,0)
	return False

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
				cb = cb.updateConstraints(i,j,sb.CurrentGameboard[i][j])

	print 'Initial:'
	for i in range(size):
		print sb.CurrentGameboard[i]

	print '\n Completed:'

	t0 = time.time()
	x = backTrackingWithMRVandMCVandLCV(sb,cb,0)
	t1 = time.time()-t0
	print t1

main()

#forward checking if any of the legalValues becomes null and isn't assigned a value then we have a problem
# so that is when it should skip testing for backtracking
'''
def test(Sudokuboard,SudokuConstraintBoard):

	print "Initial State"
	for z in range(9):
		print Sudokuboard.CurrentGameboard[z]
	print "\n"
	for x in range(9):
		print SudokuConstraintBoard.Constraints[0][x].legalVals
	for y in range(9):
		print SudokuConstraintBoard.Constraints[y][0].legalVals
	print "\n"
	print "Changed State"
	SudokuConstraintBoard = SudokuConstraintBoard.updateConstraints(0,1,1)
	for x in range(9):
		print SudokuConstraintBoard.Constraints[0][x].legalVals
	for y in range(9):
		print SudokuConstraintBoard.Constraints[y][0].legalVals
	print "\n"

	print "Changes made"
	for x in SudokuConstraintBoard.changes:
		print x

	print "\n"
	print "Back to Initial State"
	SudokuConstraintBoard= SudokuConstraintBoard.undo(0,1,1)
	for x in range(9):
		print SudokuConstraintBoard.Constraints[0][x].legalVals
	for y in range(9):
		print SudokuConstraintBoard.Constraints[y][0].legalVals
'''
