import random
import os
import time

class Map:
    '''
    A Map object holds the 'field'/setup of a specific game.
    Inputs: seed (int), boardSize (int), foodPerc (float, between 0 and 1)
    Output: Map object

    Idea: create a long string representing the map, then break it down into a 2d square array.
    0=empty, 1=food, 2=wall.
    '''
    def __init__(self, seed, boardSize, foodPerc) -> None:
        self.seed=seed
        random.seed(self.seed)
        self.size=boardSize
        assert(foodPerc <= 100 and foodPerc>=0)
        self.foodPerc=foodPerc
        size2=boardSize*boardSize
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

class Game:
    '''
    Each instance of Game holds the mechanics to run a given gene through a given map.
    Inputs: map (obj of 'Map' class), gene (str), turns (int), printing (bool)
    Outputs: score, and (optional) printing of a rerun of the game
    '''
    def __init__(self, turns:int, gene:str, printing:bool=False) -> None:
        self.turns=turns
        assert(len(gene) == 243)
        self.gene=gene
        self.print=printing
        self.score=0

    def runGame(self, map:Map):
        turn=0
        
        field=map.field
        random.seed(map.seed)
        curr=(random.randint(1,map.size+1),random.randint(1,map.size+1)) #(row,col), start on row 1, col 1. (row 0 col0 is wall)
        while (turn < self.turns):
            around=[
                field[curr[0]-1][curr[1]+0], #north
                field[curr[0]+0][curr[1]+1], #east
                field[curr[0]+1][curr[1]+0], #south
                field[curr[0]+0][curr[1]-1], #west
                field[curr[0]+0][curr[1]+0], #center
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
                if field[new[0]][new[1]] == 2: #new pos is wall
                    self.score -= 1 #minus point
                else:
                    curr=new #move to new pos
            elif action == 5: #tried to eat
                if around[4] == 1: #tile has food, give point
                    self.score +=1
                    field[curr[0]][curr[1]] = 0 #remove food from that field space.
                elif around[4]==0:
                    self.score -= 1 #tried to eat where there was no food
            turn += 1
            
            if (self.print):
                os.system('cls')
                print("Turn", turn, "Score", self.score)
                for row, rowdata in enumerate(field):
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
            print(self.score)
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





map1=Map(seed=512,boardSize=5,foodPerc=0.3)
game1=Game(
    10, '154354054254254254354354054154154154154154254154354154254354224254254224354354004054354054254254054054354054154154054154154054154354054054054004254254254354354054154354154124254254114114114154154154254254154114114114254354224254354254224224224',
    True
)
game1.runGame(map1)    
        
        




