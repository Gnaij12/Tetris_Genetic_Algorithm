import sys
from math import log
from statistics import stdev
import random
import time
SCORES = {0:0,1:40,2:100,3:300,4:1200}
# PIECES = [("I",0),("I",1),("O",0),("T",0),("T",1),("T",2),("T",3),("S",0),("S",1),("Z",0),("Z",1),("J",0),("J",1),("J",2),("J",3),("L",0),("L",1),("L",2),("L",3)]
PIECES = {"I":(0,1),"O":(0,),"T":(0,1,2,3),"S":(0,1),"Z":(0,1),"J":(0,1,2,3),"L":(0,1,2,3)}
LEFTMIDDLERIGHT = {("I",0):(0,0,0),("I",1):(3,50,50),("O",0):(1,50,1),("T",0):(1,1,1),("T",1):(2,50,1),("T",2):(0,1,0),("T",3):(1,50,2),("S",0):(1,1,0),("S",1):(1,50,2),("Z",0):(0,1,1),("Z",1):(2,50,1),("J",0):(1,1,1),("J",1):(2,50,0),("J",2):(0,0,1),("J",3):(2,50,2),("L",0):(1,1,1),("L",1):(2,50,2),("L",2):(1,0,0),("L",3):(0,50,2)}
PIECESTRINGS = {("I",0):"####",("I",1):"#\n#\n#\n#",("O",0):"##\n##",("T",0):" # \n###",("T",1):"# \n##\n# ",("T",2):"###\n # ",("T",3):" #\n##\n #",("S",0):" ##\n## ",("S",1):"# \n##\n #",("Z",0):"## \n ##",("Z",1):" #\n##\n# ",("J",0):"#  \n###",("J",1):"##\n# \n# ",("J",2):"###\n  #",("J",3):" #\n #\n##",("L",0):"  #\n###",("L",1):"# \n# \n##",("L",2):"###\n#  ",("L",3):"##\n #\n #"}

NUM_COEFFICIENTS = 5 #the number of coefficients in each strategy
COEFFICIENT_MULTIPLIER = 2
POPULATION_SIZE = 500 #the number of strategies in each generation
NUM_CLONES = 75 #the number of precisely cloned strategies retained from each generation to the next
TOURNAMENT_SIZE = 20 #how many strategies selected for each tournament
TOURNAMENT_WIN_PROBABILITY = .75 #the probability with which the best strategy in a tournament is selected
# CROSSOVER_LOCATIONS = 5 #how many exact letters from parent 1 are copied to the child in the same locations
MUTATION_RATE = .8 #the chance that a child experiences a mutation after being generated

NUM_TRIALS = 5

#Ideas for things to measure: How flat the board is (more = good?), holes, max height, average height, hole depth?, lines cleared?, closeness to top?

def printboard(board):
    print("="*21)
    # whattowrite = "="*21 + "\n"
    for i in range(20):
        # whattowrite += "|" + " ".join(board[i*10:i*10+10]) + "|\n"
        print("|" + " ".join(board[i*10:i*10+10]) + "|")
    # whattowrite += "="*21 + "\n"
    print("="*21)
    # return whattowrite
    
def elimrows(board,changedrows,maxheights):
    tempboard = board
    elimedrows = []
    for row in sorted(changedrows):
        if " " not in board[row*10:row*10+10]:
            board = " " * 10 + board[:row*10] + board[row*10+10:]
            elimedrows.append(row)
    if len(elimedrows) > 0:
        for col in maxheights.keys():
            if maxheights[col] <= row:
                found = False
                for i in range(maxheights[col]*10+col,len(board),10):
                    boardl = board[i]
                    if boardl == "#":
                        # printboard(tempboard)
                        maxheights[col] = i//10
                        found = True
                        break
                if not found:
                    maxheights[col] = 20
    return board,len(elimedrows)

def placepiece(board,i,piece,orientation,maxheights):
    width = 1 #I1
    if piece == 'O' or ((piece == "T" or piece == "J" or piece == "L") and (orientation == 1 or orientation == 3)) or ((piece == "S" or piece == "Z") and orientation == 1):
        width = 2
    elif ((piece == "T" or piece == "J" or piece == "L") and (orientation == 0 or orientation == 2)) or ((piece == "S" or piece == "Z") and orientation == 0):
        width = 3
    elif piece == "I" and orientation == 0:
        width = 4
    if i + width >10:
        return None,None,None
    left,middle,right = LEFTMIDDLERIGHT[(piece,orientation)]
    lefthit,middlehit,righthit = 50,50,50
    for col in range(i,i+width):
        blocki = maxheights[col]
        if col == i:
            lefthit = blocki-left-1
        elif col == i+width-1:
            if right == 50:
                righthit = 50
            else:
                righthit = blocki- right-1
        else:
            if middle == 50:
                middlehit = 50
            else:
                middlehit = min(blocki-middle-1,middlehit)
    if lefthit < 0 or righthit < 0 or middlehit < 0:
        return "GAME OVER",0,maxheights
    startheight = min(lefthit,righthit,middlehit)
    ps = PIECESTRINGS[(piece,orientation)]
    row = startheight
    col = i
    changedrows = [row]
    changedcols = set()
    for l in ps:
        if l == "\n":
            row+=1
            changedrows.append(row)
            col = i
        elif l == " ":
            col+=1
        elif l == "#":
            board = board[:row*10+col] + "#" + board[row*10+col+1:]
            if col not in changedcols:
                maxheights[col] = row
                changedcols.add(col)
            col+=1
    # printboard(board)
    board,elimedrows = elimrows(board,changedrows,maxheights)
    # if elimedrows > 0:
    #     for i in maxheights.keys():
    #         maxheights[i]+=elimedrows
    return board,elimedrows,maxheights

def modelall(board):
    f = open("tetrisout.txt","w")
    for i in range(10):
        for piece,orientations in PIECES:
            for o in orientations:
                # print("Piece:\n%s"%PIECESTRINGS[(piece,orientation)])
                # print()
                tempboard,score = placepiece(board,i,piece,o)
                if tempboard is not None:
                    # print("After removing:")
                    # printboard(tempboard)
                    tempboard = tempboard+"\n"
                    f.write(tempboard)

def playgame(strat):
    board = makenewboard()
    points = 0
    gameover = False
    boards = []
    maxheights = {0:20,1:20,2:20,3:20,4:20,5:20,6:20,7:20,8:20,9:20}
    while not gameover:
        boards = []
        piece = random.choice(list(PIECES.keys()))
        orientations = PIECES[piece]
        for o in orientations:
            for i in range(10):
                tempboard,tempremoved,tempmaxheights = placepiece(board,i,piece,o,maxheights.copy())
                if tempboard is not None:
                    temppoints = SCORES[tempremoved]
                    tempscore = scoreboard(tempboard,strat,tempremoved)
                    boards.append((tempboard,tempscore,temppoints,tempmaxheights))
        board,score,addpoints,maxheights = max(boards,key=lambda x:x[1])
        if board == "GAME OVER":
            gameover = True
        points+=addpoints
    return points

def playgamewithprints(strat):
    board = makenewboard()
    # f = open("test.txt","w")
    points = 0
    printboard(board)
    # f.write(printboard(board))
    gameover = False
    boards = []
    maxheights = {0:20,1:20,2:20,3:20,4:20,5:20,6:20,7:20,8:20,9:20}
    while not gameover:
        boards = []
        piece = random.choice(list(PIECES.keys()))
        orientations = PIECES[piece]
        for o in orientations:
            for i in range(10):
                tempboard,tempremoved,tempmaxheights = placepiece(board,i,piece,o,maxheights.copy())
                if tempboard is not None:
                    temppoints = SCORES[tempremoved]
                    tempscore = scoreboard(tempboard,strat,tempremoved)
                    boards.append((tempboard,tempscore,temppoints,tempmaxheights))
        board,score,addpoints,maxheights = max(boards,key=lambda x:x[1])
        if board == "GAME OVER":
            gameover = True
            print("GAME OVER")
            # f.write("GAME OVER\n")
        else:
            printboard(board)
            # f.write(printboard(board))
        points+=addpoints
        # whattowrite = "Score: " + str(points) + "\n"
        # f.write(whattowrite)
        # f.write(str(maxheights) + "\n")
        print("Score: %s" %points)
    return points

def makenewboard():
    return " "*200

def scoreboard(board,strat,removed):
    if board == "GAME OVER":
        return -1000000
    value = 0
    flat,aheight,lclear,holeswfilled,trans= strat
    allcolheights = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
    mheightused = False
    numcoveredholes = 0
    numrowswithcoveredholes = {}
    numwells = 0
    wellsdepth = 0
    deepestwell = 0
    totalholesdepth = 0
    maxheight = 0
    flatness = 0
    athashtag = False
    transitions = 0
    # currrentlyathashtag = {0:False,1:False,2:False,3:False,4:False,5:False,6:False,7:False,8:False,9:False}
    for i,l in enumerate(board):
        if i%10 == 0:
            athashtag = False
        if l == "#":
            # if not mheightused:
            #     maxheight = (20-i//10)
            #     # value += mheight * (20-i//10) if 20-i//10 != 0 else 0
            #     mheightused = True
            if allcolheights[i%10] == 0:
                allcolheights[i%10] = 20-i//10
            # currrentlyathashtag[i%10] = True
            if not athashtag and i%10 != 0:
                transitions+=1
            athashtag = True
        if l == " ":
            if allcolheights[i%10] != 0:
                # if currrentlyathashtag[i%10]:
                numcoveredholes+=1
                totalholesdepth += allcolheights[i%10]-(20-i//10)
                    # currrentlyathashtag[i%10] = False
                if i%10 not in numrowswithcoveredholes:
                    numrowswithcoveredholes[i%10] = 1
            if athashtag:
                transitions+=1
            athashtag = False
    for i,depth in allcolheights.items():
        if i+1 in allcolheights:
            flatness+= abs(allcolheights[i]-allcolheights[i+1])
        if ((i-1 in allcolheights and depth < allcolheights[i-1]) or i-1 not in allcolheights) and ((i+1 in allcolheights and depth < allcolheights[i+1]) or i+1 not in allcolheights): #checks if the height to the right and left is greater
            numwells+=1
            wellsdepth+= min(allcolheights[i-1] if i-1 in allcolheights else 21,allcolheights[i+1] if i+1 in allcolheights else 21)-depth
            deepestwell = max(deepestwell,min(allcolheights[i-1] if i-1 in allcolheights else 21,allcolheights[i+1] if i+1 in allcolheights else 21)-depth)
    # standardev = stdev(list(allcolheights.values()))
    # value += flat * standardev
    value += flat * flatness
    # value += wells * numwells 
    average = sum(allcolheights.values())#/len(allcolheights) 
    value += aheight * average
    # value += closenesstomiddle * (10-abs(average-10)) #Closer = higher value
    # value += wdepth * wellsdepth
    # value += deepwell * deepestwell
    value += lclear * removed
    value += holeswfilled * numcoveredholes * numcoveredholes
    # value += holesdepth * totalholesdepth
    # value += rowswithcoveredholes * len(numrowswithcoveredholes)
    # value += tetris * 10
    value += trans * transitions
    return value

def fitness(strat):
    scores = []
    for i in range(NUM_TRIALS):
        scores.append(playgame(strat))
    return sum(scores)/len(scores)

def makechild(parent1,parent2):
    numcrosses = random.choice(range(1,len(parent1)-1))
    crosses = random.sample(range(len(parent1)),numcrosses)
    child = [None]*len(parent1)
    for i in crosses:
        child[i] = parent1[i]
    for i,n in enumerate(parent2):
        if child[i] == None:
            child[i] = n
    if random.random() < MUTATION_RATE:
        mutation = random.choice(range(len(child)))
        # child[mutation] = random.random()*2-1
        child[mutation] += random.random()*COEFFICIENT_MULTIPLIER-.2*COEFFICIENT_MULTIPLIER
        if child[mutation] >= 1*COEFFICIENT_MULTIPLIER:
            child[mutation] = 1*COEFFICIENT_MULTIPLIER
        elif child[mutation] <= -1*COEFFICIENT_MULTIPLIER:
            child[mutation] = -1*COEFFICIENT_MULTIPLIER
    return tuple(child)

def continuegenetic(strats,stratslist):
    newstratslist = []
    newstrats = set()
    for i in range(NUM_CLONES):
        clonestrat,clonefitval = stratslist[i]
        fitval = fitness(clonestrat)
        newstratslist.append((clonestrat,fitval))
        newstrats.add(clonestrat)
        print("Strat %s Fitness: %s"%(len(newstratslist),fitval))
    while len(newstratslist) < POPULATION_SIZE:
        tourny = random.sample(stratslist,TOURNAMENT_SIZE*2)
        tourny1 = tourny[:len(tourny)//2]
        tourny1 = sorted(tourny1,key=lambda x:x[1],reverse=True)
        tourny2 = tourny[len(tourny)//2:]
        tourny2 = sorted(tourny2,key=lambda x:x[1],reverse=True)
        parent1 = tuple()
        parent2 = tuple()
        for i in range(len(tourny1)):
            if random.random() < TOURNAMENT_WIN_PROBABILITY or i == len(tourny1)-1:
                parent1 = tourny1[i][0]
                break
        for i in range(len(tourny2)):
            if random.random() < TOURNAMENT_WIN_PROBABILITY or i == len(tourny2)-1:
                parent2 = tourny2[i][0]
                break
        child = makechild(parent1,parent2)
        if child not in newstrats:
            fitval = fitness(child)
            newstratslist.append((child,fitval))
            newstrats.add(child)
            print("Strat %s Fitness: %s"%(len(newstratslist),fitval))
    return newstrats,sorted(newstratslist,key=lambda x:x[1],reverse=True)

def startgenetic():
    strats = set()
    stratslist = []
    while len(stratslist) < POPULATION_SIZE:
        strat = tuple([random.random()*2*COEFFICIENT_MULTIPLIER-1*COEFFICIENT_MULTIPLIER for i in range(NUM_COEFFICIENTS)])
        # strat = random.sample(range(-1,1,.1),NUM_COEFFICIENTS)
        if strat not in strats:
            fitval = fitness(strat)
            strats.add(strat)
            stratslist.append((strat,fitval))
            print("Strat %s Fitness: %s"%(len(stratslist),fitval))
    stratslist = sorted(stratslist,key=lambda x:x[1],reverse=True)
    return strats,stratslist

def loadgenetic(filename):
    strats = set()
    stratslist = []
    with open(filename) as f:
        genloaded = False
        for line in f:
            if genloaded:
                strat = eval(line.split("_")[0])
                fitnessval = line.split("_")[1]
                score = float(fitnessval[:len(fitnessval)-1])
                strats.add(strat)
                stratslist.append((strat,score))
            else:
                generation = int(line)
                genloaded = True
    return strats,stratslist,generation

def rungenetic(strats,stratslist,generation):
    correct = False
    while not correct:
        choice = input("Do you want to watch a game from the best strategy, save this generation, or continue to evolve another generation?\nb if watch best, s if save, c to continue ").lower()
        if choice == "b":
            # strat = stratslist[0][0]
            # temp = fitness(stratslist[0][0])
            playgamewithprints(stratslist[0][0])
            correct = True
        elif choice == "s":
            filename = input("What file do you want to store in?\n")
            f = open(filename,"w")
            whattowrite = str(generation) + "\n"
            f.write(whattowrite)
            for strat in stratslist:
                whattowrite = str(strat[0]) + "_" + str(strat[1]) + "\n"
                f.write(whattowrite)
            return
        elif choice == "c":
            strats,stratslist = continuegenetic(strats,stratslist)
            generation+=1
            print("Generation %s"%generation)
            print("Best coefficients: %s   Score: %s" %(str(stratslist[0][0]),str(stratslist[0][1])))
            start = time.perf_counter()
            total = sum(x[1] for x in stratslist)
            print("Average Score: %s" %(total/len(stratslist)))
            correct = True
        else:
            print("%s is not an option." %choice)
    rungenetic(strats,stratslist,generation)


# board = "          #         #         #      #  #      #  #      #  #     ##  #     ##  #     ## ##     ## #####  ########  ######### ######### ######### ######### ########## #### # # # # ##### ###   ########"
# printboard(board)
# score = scoreboard(board,(0,)*NUM_COEFFICIENTS,0)
correct = False
while not correct:
    neworload = input("Do you want to start a new genetic process or load a saved one?\nType n if new and s if load saved. ").lower()
    if neworload == "n":
        correct = True
    elif neworload == "s":
        filename = input("Type the name of the file you want to load from. ")
        correct = True
    else: 
        print("%s is not an option." %neworload)
strats,stratslist = set(),[]
generation = 0
if neworload == "n":
    start = time.perf_counter()
    strats,stratslist = startgenetic()
    print("Time taken: %s" %(time.perf_counter()-start))
    print("Generation %s"%generation)
    print("Best coefficients: %s   Score: %s" %(str(stratslist[0][0]),str(stratslist[0][1])))
    total = sum(x[1] for x in stratslist)
    print("Average Score: %s" %(total/len(stratslist)))
else:
    strats,stratslist,generation = loadgenetic(filename)
    print("Generation %s"%generation)
    print("Best coefficients: %s   Score: %s" %(str(stratslist[0][0]),str(stratslist[0][1])))
    # start = time.perf_counter()
    total = sum(x[1] for x in stratslist)
    print("Average Score: %s" %(total/len(stratslist)))
rungenetic(strats,stratslist,generation)
# board = sys.argv[1]
# # printboard(board)
# modelall(board)