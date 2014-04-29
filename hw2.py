from sudoku import *
import math,random,copy,time,os

####Helper classes
class Constraint():
	def __init__(self,legalVals,isAssigned):
		self.legalVals = legalVals
		self.isAssigned= isAssigned

class ConstraintBoard():
	def __init__(self,size,constraints):
		self.BoardSize=size
		self.Constraints = constraints

	def updateConstraints(self,row,col,val):
		self.Constraints[row][col].isAssigned = True
		self.Constraints[row][col].legalVals.remove(val)
		subsquare = int(math.sqrt(self.BoardSize))
		#update the row
		for i in range(self.BoardSize):
			if i!=col:
				if val in self.Constraints[row][i].legalVals:
					self.Constraints[row][i].legalVals.remove(val)
		#update the col
		for j in range(self.BoardSize):
			if j!=row:
				if val in self.Constraints[j][col].legalVals:
					self.Constraints[j][col].legalVals.remove(val)
		#update the subsquare
		squareRow = row // subsquare
		squareCol = col // subsquare
		for i in range(subsquare):
			for j in range(subsquare):
				x = squareRow*subsquare+i
				y = squareCol*subsquare+j
				if x!=row and y != col:
					if val in self.Constraints[x][y].legalVals:
						self.Constraints[x][y].legalVals.remove(val)
		return ConstraintBoard(self.BoardSize,self.Constraints)

##########
##########
#CSP Related Functions
def forwardCheck(cb):#return false if no legalValues for a cell else true
	size = cb.BoardSize
	for i in range(size):
		for j in range(size):
			if cb.Constraints[i][j].isAssigned==False and not cb.Constraints[i][j].legalVals:
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
#MCV = most constraining variable
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
					if not cb.Constraints[row][i].isAssigned: 
						mcv +=1
			for j in range(size):#col search
				if j!=row:
					if not cb.Constraints[j][col].isAssigned:
						mcv+=1
			squareRow = row // subsquare
			squareCol = col // subsquare
			for i in range(subsquare):#subsquare search
				for j in range(subsquare):
					x = squareRow*subsquare+i
					y = squareCol*subsquare+j
					if x!= row and y!=col:
						if not cb.Constraints[x][y].isAssigned:
							mcv+=1
			if mcv>maxMCV:
				maxMCV=mcv
				(optRow,optCol) = (row,col)
	return (optRow,optCol)

def leastConstrainingValue(row,col,cb):
	lVals = cb.Constraints[row][col].legalVals
	if len(lVals)==1:
		return {0 : lVals[0]}

	size=cb.BoardSize
	subsquare = int(math.sqrt(size))
	lcvDict = {}

	for val in lVals:
		lcvDict[constrainScore(row,col,val,cb,size)] = val
	return lcvDict

def constrainScore(row,col,val,cb,size):
	score=0
	subsquare = int(math.sqrt(size))
	for i in range(size):
		if i!=col:
			if not cb.Constraints[row][i].isAssigned and  val in cb.Constraints[row][i].legalVals:
				score+=len(cb.Constraints[row][i].legalVals)-1
	for j in range(size):
		if j !=row:
			if not cb.Constraints[j][col].isAssigned and  val in cb.Constraints[j][col].legalVals:
				score+=len(cb.Constraints[j][col].legalVals)-1
	squareRow = row // subsquare
	squareCol = col // subsquare
	for i in range(subsquare):
		for j in range(subsquare):
			x = squareRow*subsquare+i
			y = squareCol*subsquare+j
			if x!= row and y!=col:
				if not cb.Constraints[x][y].isAssigned and val in cb.Constraints[x][y].legalVals:
					score+=len(cb.Constraints[row][i].legalVals)-1
	return score

############
############
#Different Backtracking functions
def backTrackingWithMRVandMCVandLCV(Sudokuboard,SudokuConstraintBoard,variable_assign):
	if iscomplete(Sudokuboard.CurrentGameboard):
		for i in range(Sudokuboard.BoardSize): 
			print Sudokuboard.CurrentGameboard[i]
		print variable_assign
		return True
	else:
		(row,col) = getEmptySquareMRVAndMCV(SudokuConstraintBoard)
		lcvDict = leastConstrainingValue(row,col,SudokuConstraintBoard)
		sortedKeys = sorted(lcvDict.iterkeys(),reverse=True)
		for i in sortedKeys:
			variable_assign +=1
			Sudokuboard = Sudokuboard.set_value(row,col,lcvDict[i])
			myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
			myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,lcvDict[i])
			if forwardCheck(myCopyOfCBoard):
				if backTrackingWithMRVandMCVandLCV(Sudokuboard,
					myCopyOfCBoard,
					variable_assign):
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
		(row,col) = getEmptySquareMRVAndMCV(SudokuConstraintBoard)
		legalVals = SudokuConstraintBoard.Constraints[row][col].legalVals
		for v in legalVals:
			variable_assign +=1
			Sudokuboard = Sudokuboard.set_value(row,col,v)
			myCopyOfCBoard = copy.deepcopy(SudokuConstraintBoard)
			myCopyOfCBoard = myCopyOfCBoard.updateConstraints(row,col,v)
			if forwardCheck(myCopyOfCBoard):
				if backTrackingWithMRVandMCV(Sudokuboard,
					myCopyOfCBoard,
					variable_assign):
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
			if forwardCheck(myCopyOfCBoard):
				if backTrackingWithFC(Sudokuboard,
					myCopyOfCBoard,
					variable_assign):
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
			if simpleBackTracking(Sudokuboard,
				myCopyOfCBoard,
				variable_assign):
				return True
			Sudokuboard = Sudokuboard.set_value(row,col,0)
	return False

"""
def main():
	#initialize environment
	file_name= 'testFiles/9x9.20.txt'
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
"""

def test():
	path = os.getcwd()+"/testFiles"
	files = []
	for root,dirs,files in os.walk(path):
		pass
	for f in files:
		file_name = os.path.join("testFiles/",f)
		sb = init_board(file_name)
		size = sb.BoardSize
		domain = []
		if size == 4:
			constraints = [[Constraint([1,2,3,4],False) for i in range(size)] for x in range(size)]
		elif size == 9:
			constraints = [[Constraint([1,2,3,4,5,6,7,8,9],False) for i in range(size)] for x in range(size)]
		elif size ==16:
			constraints = [[Constraint([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],False) for i in range(size)] for x in range(size)] 
		else:
			constraints = [[Constraint([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],False)
			for i in range(size)] for x in range(size)] 


		cb = ConstraintBoard(size,constraints)
		for i in range(size):
			for j in range(size):
				if sb.CurrentGameboard[i][j]!=0:
					cb = cb.updateConstraints(i,j,sb.CurrentGameboard[i][j])

		print "______________________________________\n"
		print "Filename: "+ f+"\n"
		print 'Initial:'
		for i in range(size):
			print sb.CurrentGameboard[i]

		print '\n Completed:'

		t0 = time.time()
		x = backTrackingWithMRVandMCVandLCV(sb,cb,0)
		t1 = time.time()-t0
		print t1

test()
