from itertools import starmap
import MyCla
import os       # to open all files: settings, results, etc
import json     # to read the results file and resume the game
import random   # To generate gene pool from scratch
import multiprocessing as mp # To split running simulation across all CPU cores
import time

#Manual parameters
popSize = 10
scorefile = "zscores.csv"
foodPerc = 30
seed = random.randint(0,999999)
boardSize=5
foodPerc=0.3
turns=100

def evol():
    # tracker vars
    gen = 0
    allGenHigh = 0
    currGenHigh = 0
    
    # operational vars
    map = MyCla.Map(seed,boardSize,foodPerc)
    players = [MyCla.Player() for i in range(popSize)] #randomly creates genes
    games = [MyCla.Game(turns, player, map) for player in players] #create games based on the map and players provided
    test=True
    while test:
        test=False
        #multiprocess runner
        st = time.time()
        p = mp.Pool(int(mp.cpu_count()))
        fastRes = p.map(MyCla.Game.runGame, games)
        p.close()
        p.join()
        print(fastRes)


        # st4 = time.time()
        # for n in range(loops):
        #     p = mp.Pool(int(mp.cpu_count()))
        #     futures = [p.map_async(t.runGame,()) for t in games]
        #     p.close()
        #     p.join()
        #     #result = [fut.get() for fut in futures]
        # t4=time.time()- st4
        # print (t4)
        
        #print(futures)
        #result = [fut.get() for fut in futures]
        #result = p.map([game.runGame for game in games], ())

        #print(futures)

if __name__ == '__main__':
    evol()
# map1=Map(seed=512,boardSize=5,foodPerc=0.3)
# game1=Game(
#     10, '154354054254254254354354054154154154154154254154354154254354224254254224354354004054354054254254054054354054154154054154154054154354054054054004254254254354354054154354154124254254114114114154154154254254154114114114254354224254354254224224224',
#     True
# )
# game1.runGame(map1)    
        