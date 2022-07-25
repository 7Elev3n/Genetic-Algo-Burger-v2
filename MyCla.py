from distutils.ccompiler import gen_lib_options
import random
import os
import time
import pickle
import csv

class Map:
    '''
    A Map object holds the 'field'/setup of a specific game.
    Inputs: seed (int), boardSize (int), foodPerc (float, between 0 and 1)
    Output: Map object
    0=empty, 1=food, 2=wall.
    '''
    def __init__(self, seed, boardSize, foodPerc, **kwargs) -> None:
        self.seed=seed
        random.seed(self.seed)
        self.size=boardSize
        assert(foodPerc <= 100 and foodPerc>=0)
        self.foodPerc=foodPerc
        size2=self.size*self.size
        noWallList=random.choices(
            population=[0,1],
            weights=[1-foodPerc,foodPerc],
            k=size2
        )
        #Constructing the 2D map
        self.field=[[2]*(self.size+2)]
        for i in range(self.size):
            (start, end) = ((self.size)*i,(self.size)*(i+1))
            self.field.append([2]+noWallList[start:end]+[2])
        self.field.append([2]*(self.size+2))
    
    def update(self, **kwargs):
        '''
        Possible attributes include: 'seed', 'size', 'foodPerc', 'field'.
        '''
        # Code to update self attributes via **kwargs
        allowed_keys = {'seed', 'size', 'foodPerc', 'field'}
        for attr, value in kwargs.items():
            if attr in allowed_keys:
                setattr(self, attr, value)
            else:
                raise Exception("'Map' instance updated with out-of-bounds attribute: "+str(attr))

class Player:
    '''
    Holds the gene, and reproductive functions.
    Inputs: reproductive parameters
    '''
    def __init__(self,gene=0) -> None:
        if gene == 0:
            #assume this is a new gene line
            genelist = random.SystemRandom().choices(range(0,6),k=243)
            gene= "".join(str(i) for i in genelist)
        self.gene=gene

    def reproduce(self, partner:str, nChildren:int, nMutations):
        partnergene=partner
        children=[]
        for i in range(nChildren):
            crossPoint = random.SystemRandom().randint(0,242)
            child = Player(gene=self.gene[:crossPoint]+partner[crossPoint:])
            actualMutations=random.SystemRandom().randint(0,int(nMutations))
            for mut in range(actualMutations):
                mutpt=random.SystemRandom().randint(0,242)
                child =  child[:mutpt-1] + random.SystemRandom().choice(['0','1','2','3','5']) + child[(mutpt):]
            children.append(child)
        return children

class Game:
    '''
    Each instance of Game holds the mechanics to run a given gene through a given map.
    Inputs: map (obj of 'Map' class), gene (str), turns (int), printing (bool)
    Outputs: score, and (optional) printing of a rerun of the game
    '''
    def __init__(self, turns:int, player:Player, map:Map, printing:bool=False) -> None:
        self.turns=turns
        assert(len(player.gene) == 243)
        self.player = player
        self.gene=player.gene
        self.print=printing
        self.score=0
        self.field=map.field
        self.size=map.size
        self.seed=random.seed(map.seed)
    
    def update(self, **kwargs):
        '''
        Possible attributes include: 'turns', 'player', (player) 'gene', 'print', 'score', (map) 'field', 'size', 'seed'.
        '''
        # Code to update self attributes via **kwargs
        allowed_keys = {'turns', 'player', 'gene', 'print', 'score', 'field', 'size', 'seed'}
        for attr, value in kwargs.items():
            if attr in allowed_keys:
                setattr(self, attr, value)
            else:
                raise Exception("'Game' instance updated with out-of-bounds attribute: "+str(attr))

    def runGame(self):
        turn=0
        curr=(random.randint(1,(self.size)-1),random.randint(1,(self.size)-1)) #(row,col), start on row 1, col 1. (row 0 col0 is wall)
        while (turn < self.turns):
            around=[
                self.field[curr[0]-1][curr[1]+0], #north
                self.field[curr[0]+0][curr[1]+1], #east
                self.field[curr[0]+1][curr[1]+0], #south
                self.field[curr[0]+0][curr[1]-1], #west
                self.field[curr[0]+0][curr[1]+0], #center
            ]
            strAround = "".join(str(x) for x in around)
            action = int(self.gene[int(strAround, base=3)])
            match action:
                case 0: #move north
                    new=[curr[0]-1,curr[1]+0]
                case 1: #move east
                    new=[curr[0]-1,curr[1]+0]
                case 2: #move south
                    new=[curr[0]-1,curr[1]+0]
                case 3: #move west
                    new=[curr[0]-1,curr[1]+0]
                case 4 | 5: #no movement or eat at current location
                    new=curr
            
            if action in [0,1,2,3,4]: #tried to move or stay put
                if self.field[new[0]][new[1]] == 2: #new pos is wall
                    self.score -= 0.1 #minus point
                else:
                    curr=new #move to new pos
            elif action == 5: #tried to eat
                if around[4] == 1: #tile has food, give point
                    self.score +=1
                    self.field[curr[0]][curr[1]] = 0 #remove food from that field space.
                elif around[4]==0:
                    self.score -= 0.1 #tried to eat where there was no food
            turn += 1
            
            if (self.print):
                os.system('cls')
                print("Turn", turn, "Score", self.score)
                for row, rowdata in enumerate(self.field):
                    for col, itm in enumerate(rowdata):
                        if row == curr[0] and col == curr[1]:
                            print("X", end=" ")
                        else:
                            if itm == 0:
                                print(" ",end=" ")
                            if itm == 1:
                                print(".",end=" ")
                            if itm == 2:
                                print("#",end=" ")
                    print()
                time.sleep(0.2)
        if self.print == False:
            return(self)
            '''
                  ☐   
                W F ☐  
                  F  

                ==> N:0, E:0, S:1, W:2, C:1  
                ==> 00121: base 3 int  
                ==> 16: base 10 int (= int('00121', base=3))  
                ==> 16th digit of player/gene read
                Range of this function:
                0 <= int('str', base=3) <= 241
            '''
class SimState:
    def __init__(self, seed:int, boardSize:int, foodPerc:float, popSize:int, turns:int) -> None:
        #if pickle file present, load from there and return. else regenerate new.
        if os.path.exists('savefile.pkl') and input("Savefile found. Resume? Y/N") in ["yes", "Yes", "Y", "y"]:
            with open('savefile.pkl', 'wb') as savefile:
                self = pickle.load(self, savefile, pickle.HIGHEST_PROTOCOL)
            myattrs = [x for x in  dir(self) if x[0] != "_"]
            print("These are the attributes recovered from the savefile: ", [(x, getattr(self, x)) for x in dir(self) if x[0] != "_"])
            print("These attributes were set to:")
            for x in myattrs:
                print(x, " : ", getattr(self, x))
            if input("Should the simulation proceed? Y/N") not in ["yes", "Yes", "Y", "y"]:
                return
        else:
            self.gen=0
            self.map=Map(seed,boardSize,foodPerc)
            self.players=[Player() for i in range(popSize)] #randomly creates genes
            self.games=[Game(turns, player, map) for player in self.players] #create games based on the map and players provided
            self.allGenHigh=0
            self.currGenHigh=0

            myattrs = [x for x in  dir(self) if x[0] != "_"]
            print("No save file was found. \nThese are the (new) values for this simulation's attributes: ", [(x, getattr(self, x)) for x in dir(self) if x[0] != "_"])
            print("These attributes were set to:")
            for x in myattrs:
                print(x, " : ", getattr(self, x))
            if input("Should the simulation proceed? Y/N") not in ["yes", "Yes", "Y", "y"]:
                return
    
    def update(self, **kwargs):
        '''
        Possible attributes include: 'gen', 'map', 'players' (list), 'games' (list), 'allGenHigh', 'currGenHigh'.
        '''
        # Code to update self attributes via **kwargs
        allowed_keys = {'gen', 'map', 'players', 'games', 'allGenHigh', 'currGenHigh'}
        for attr, value in kwargs.items():
            if attr in allowed_keys:
                setattr(self, attr, value)
            else:
                raise Exception("'SimState' instance updated with out-of-bounds attribute: "+str(attr))
    
    def update(self, **kwargs):
        '''
        Use this to set 'map' (if changing) and 'players'. The rest should be directly updated.
        '''
        # Code to update self attributes via **kwargs
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def save(self):
        with open('savefile.pkl', 'wb') as savefile:
            pickle.dump(self, savefile, pickle.HIGHEST_PROTOCOL)
    
    def track(self):
        with open("scorefile.csv", "a+", newline='',) as scorefile:
            #Collect all stateVars and turn into dict so it can be auto populated into csv by DictWriter
            allStateVars = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
            allValues = [getattr(self, stateVar) for stateVar in allStateVars]
            dictToWrite = dict(zip(allStateVars, allValues))
            writer = csv.DictWriter(scorefile,fieldnames=allStateVars)
            writer.writerow(dictToWrite)
        

# map1=Map(seed=512,boardSize=5,foodPerc=0.3)
# game1=Game(
#     10, '154354054254254254354354054154154154154154254154354154254354224254254224354354004054354054254254054054354054154154054154154054154354054054054004254254254354354054154354154124254254114114114154154154254254154114114114254354224254354254224224224',
#     True
# )
# game1.runGame(map1)    
        
        




