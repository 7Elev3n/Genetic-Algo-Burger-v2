import MyCla
import os       # to open all files: settings, results, etc
import json     # to read the results file and resume the game
import random   # To generate gene pool from scratch
import multiprocessing as mp # To split running simulation across all CPU cores
import time
import pickle
import csv
import sys # for exiting out at any time

#evolution params
turns=20
popSize = 2000 #typically contains several hundreds or thousands of possible solutions
mutations = 0.15
bestToRemain = 0.1
inequity = 0.1 # set between 0 and 1. "0.2" means that a bot doing 100 points better than others gets a 20 times higher chance to be a parent.
childPerCouple = 0.10 #all couples get to make 10% of whatever space is left in the population by the time their turn arrives.

class GenEvol:
    '''
    This class holds all the Genetic Evolution code, the state of the simulation, and all starting parameters.

    Run specific functions from this class to move the simulation forward.
    '''
    def __init__(self, seed:int, boardSize:int, foodPerc:float, popSize:int, turns:int, mutations:float, bestToRemain:float, inequity:float, childPerCouple:float) -> None:
        #if pickle file present, load from there and return. else regenerate new.
        if os.path.exists('savefile.pkl') and input("Savefile found. Resume? Y/N") in ["yes", "Yes", "Y", "y"]:
            with open('savefile.pkl', 'rb') as savefile:
                self.__dict__ = pickle.load(savefile)
            myattrs = [x for x in  dir(self) if x[0] != "_"]
            print("-------- A savefile was found AND loaded. --------")
            self.initialPrint()
            self.newcsv = False
        else:
            # State Variables
            # variables starting with V are not to be tracked in the csv
            self.popSize=popSize
            self.foodPerc=foodPerc
            self.allGenHigh=0
            self.currGenHigh=0
            self.mutations = mutations
            self.bestToRemain = bestToRemain
            self.inequity = inequity
            self.childPerCouple = childPerCouple
            self.gen=0
            self.Vnewcsv = True
            
            #initialise world vars
            self.Vmymap=MyCla.Map(seed,boardSize,foodPerc) #THIS MEANS MAP CANNOT BE UPDATED ONCE GAME STARTS UNLESS U DIRECTLY REFERENCE AND CHANGE IT.
            self.Vplayers=[MyCla.Player() for i in range(popSize)] #randomly creates genes
            self.Vgames=[MyCla.Game(turns, player, self.Vmymap) for player in self.Vplayers] #create games based on the map and Vplayers provided
            
            

            print("-------- A savefile was NOT found. --------")
            self.initialPrint()

            
    def initialPrint(self):
        myattrs = [x for x in  dir(self) if x[0] != "_"]
        print("These are the simulation's attributes: ", [x for x in dir(self) if x[0] != "_"])

        print("These attributes were set to:")

        for x in myattrs:
            if x in ['allGenHigh', 'bestToRemain', 'childPerCouple', 'currGenHigh', 'foodPerc', 'gen', 'inequity', 'mutations', 'popSize']:
                print(x, "\t: ", getattr(self, x))
        
        if input("Should the simulation proceed? Y/N") not in ["yes", "Yes", "Y", "y"]:
            sys.exit("Human entered NO.")
        print()

    def save(self):
        with open('savefile.pkl', 'wb') as savefile:
            pickle.dump(self.__dict__, savefile, pickle.HIGHEST_PROTOCOL)
    
    def track(self):
        with open("scorefile.csv", "a+", newline='',) as scorefile:
            #Collect all stateVars and turn into dict so it can be auto populated into csv by DictWriter
            allStateVars = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and not attr.startswith("V")]
            allValues = [getattr(self, stateVar) for stateVar in allStateVars]
            dictToWrite = dict(zip(allStateVars, allValues))
            writer = csv.DictWriter(scorefile,fieldnames=allStateVars)
            if self.Vnewcsv != False:
                writer.writeheader()
                self.Vnewcsv=False
            writer.writerow(dictToWrite)

    def runGames(self):
        # Run self.games in parallel
        gamePool = mp.Pool(int(mp.cpu_count()))
        self.VfinGames = gamePool.map(MyCla.Game.runGame, self.Vgames)
        gamePool.close()
        gamePool.join()

    def sortGames(self):
        # Sort already-run games
        self.VsortedGames = sorted(self.VfinGames, key=lambda x: x.score, reverse=True) # descending
        self.currGenHigh = self.VsortedGames[0].score
        if self.currGenHigh > self.allGenHigh: 
            self.allGenHigh = self.currGenHigh
    
    def geneAlgo(self):
        self.VnewGen=[]
        # keep some elites
        for n in range(round(self.bestToRemain*self.popSize)):
            self.VnewGen.append(self.VsortedGames[n].player)
        # Find and weight parents in a list based on their relative performance
        offset = self.VsortedGames[-1].score
        weights = [round((player.score-offset)*self.inequity)+1 for player in self.VsortedGames]
        self.parentsGameList = random.sample(self.VsortedGames, self.popSize, counts=weights)
    
    def offspringMaker(self):
        while len(self.VnewGen) < self.popSize:
            nChild = round(self.childPerCouple*(self.popSize-len(self.VnewGen)))+1
            player1 = self.parentsGameList[0].player
            gene2 = random.choice(self.parentsGameList).gene
            self.VnewGen.extend(player1.reproduce(gene2, nChildren=nChild, nMutations=self.mutations))
            del(self.parentsGameList[0])
        del(self.parentsGameList)
    
    def newCycle(self):
        self.gen+=1
        self.Vplayers=self.VnewGen
        self.save()
        self.track()

        print("Current Generation:", self.gen)
        print("Current Generation Top: ", self.currGenHigh)
        print("All Generation Top: ", self.allGenHigh)
        print("---------")

if __name__ == '__main__':
    # Let there be light
    myWorld = GenEvol(
        seed=711,
        boardSize=5,
        foodPerc=0.2,
        popSize=2000,
        turns=15,
        mutations=0.15,
        bestToRemain=0.1,
        inequity=0.1,
        childPerCouple=0.1
    )
    running=True
    # run the simulation
    while running:
        try:
            myWorld.runGames()
            myWorld.sortGames()
            myWorld.geneAlgo()
            myWorld.offspringMaker()
            myWorld.newCycle()
        except KeyboardInterrupt:
            print("Interrupted")
            




# map1=Map(seed=512,boardSize=5,foodPerc=0.3)
# game1=Game(
#     10, '154354054254254254354354054154154154154154254154354154254354224254254224354354004054354054254254054054354054154154054154154054154354054054054004254254254354354054154354154124254254114114114154154154254254154114114114254354224254354254224224224',
#     True
# )
# game1.runGame(map1)    
        