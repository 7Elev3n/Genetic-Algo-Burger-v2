from itertools import starmap
import MyCla
import os       # to open all files: settings, results, etc
import json     # to read the results file and resume the game
import random   # To generate gene pool from scratch
import multiprocessing as mp # To split running simulation across all CPU cores
import time

#Manual parameters
scorefile = "zscores.csv"
foodPerc = 30
seed = 512 #random.randint(0,999999)
boardSize=5
foodPerc=0.3

#evolution params
turns=20
popSize = 2000 #typically contains several hundreds or thousands of possible solutions
mutations = 0.15
bestToRemain = 0.1
inequity = 0.1 # set between 0 and 1. "0.2" means that a bot doing 100 points better than others gets a 20 times higher chance to be a parent.
childPerCouple = 0.10 #all couples get to make 10% of whatever space is left in the population by the time their turn arrives.

def evol():
    # tracker vars
    gen = 0
    allGenHigh = 0
    currGenHigh = 0
    
    # operational vars
    map = MyCla.Map(seed,boardSize,foodPerc)
    players = [MyCla.Player() for i in range(popSize)] #randomly creates genes
    running=True
    
    while running:
                


        #test=False #run it once only
        games = [MyCla.Game(turns, player, map) for player in players] #create games based on the map and players provided

        #multiprocess runner
        p = mp.Pool(int(mp.cpu_count()))
        finGames = p.map(MyCla.Game.runGame, games)
        p.close()
        p.join()
        sortedGames = sorted(finGames, key=lambda x: x.score, reverse=True) # descending
        currGenHigh = sortedGames[0].score
        if currGenHigh > allGenHigh: allGenHigh = currGenHigh

        # genetic algo
        newGen = []
        # keep some elites
        for n in range(round(bestToRemain*popSize)):
            newGen.append(sortedGames[n].player)
        # Find and weight parents in a list based on their relative performance
        offset = sortedGames[-1].score
        weights = [round((player.score-offset)*inequity)+1 for player in sortedGames]
        parentsGameList = random.sample(sortedGames, popSize, counts=weights)

        while len(newGen) < popSize:
            nChild = round(childPerCouple*(popSize-len(newGen)))+1
            player1 = parentsGameList[0].player
            gene2 = random.choice(parentsGameList).gene
            newGen.extend(player1.reproduce(gene2, nChildren=nChild, nMutations=mutations))
            del(parentsGameList[0])
        players=newGen
        print("Current Generation:", gen)
        print("Current Generation Top: ", currGenHigh)
        print("All Generation Top: ", allGenHigh)
        print("---------")
        gen+=1


if __name__ == '__main__':
    evol()
# map1=Map(seed=512,boardSize=5,foodPerc=0.3)
# game1=Game(
#     10, '154354054254254254354354054154154154154154254154354154254354224254254224354354004054354054254254054054354054154154054154154054154354054054054004254254254354354054154354154124254254114114114154154154254254154114114114254354224254354254224224224',
#     True
# )
# game1.runGame(map1)    
        