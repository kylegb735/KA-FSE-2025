from pygame import *
from glob import *
from random import *
from math import *

screen = display.set_mode((1600,900))

def getMoves(sprite): 
    moves = []
    for move in glob(f"Images/Enemies/{sprite}/*"):
        moves.append(move.split('\\')[-1])
    print(moves)
    return moves

def getPics(sprite, moves):
    enemyPics = []
    for move in moves:
        movePics = []
        picNames = glob(f"Images/Enemies/{sprite}/{move}/*.png")
        for picName in picNames:
            movePics.append(image.load(picName))
        enemyPics.append(movePics)
    return enemyPics

def generateEnemy():
    type = randint(0, len(enemyTypes) - 1) # randomly select an enemy type
    enemies.append([randint(100, 1100), randint(100, 700), enemyTypes[type][0], enemyTypes[type][1], enemyTypes[type][2], enemyTypes[type][3], enemyTypes[type][4], enemyTypes[type][5]])

def doMove(sprite, move):
    index = sprite[MOVES].index(move)
    idle = sprite[MOVES].index('Idle')
    if sprite[MOVE] == idle:
        sprite[MOVE] = index
        sprite[FRAME] = 0
    elif sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle

def damage(sprite, amount):
    sprite[HEALTH] -= amount
    if sprite[HEALTH] <= 0:
        sprite[HEALTH] = 0

def kill(sprite):
    enemies.remove(sprite)

def updateSprite(sprite):
    sprite[FRAME] += 0.2
    idle = sprite[MOVES].index('Idle')

    if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle
    print(sprite[MOVE], sprite[FRAME])

def drawSprite(sprite):
    pic = sprite[PICS][sprite[MOVE]][int(sprite[FRAME])]
    screen.blit(pic, (sprite[X] - pic.get_width() // 2  , sprite[Y] - pic.get_height() // 2))

NAME = 0
MOVE = 1
FRAME = 2
HEALTH = 3
MOVES = 4
PICS = 5

#            name         move  frame health
berserker = ['berserker', 6   , 0   , 130]
berserker.append(getMoves(berserker[NAME]))
berserker.append(getPics(berserker[NAME], berserker[MOVES]))

shaman = ['shaman', 6   , 0, 70]
shaman.append(getMoves(shaman[NAME]))
shaman.append(getPics(shaman[NAME], shaman[MOVES]))

warrior = ['warrior', 6   , 0, 100]
warrior.append(getMoves(warrior[NAME]))
warrior.append(getPics(warrior[NAME], warrior[MOVES]))

enemyTypes = [berserker, shaman, warrior]
enemies = []
for i in range(30):
    generateEnemy()
print(enemies)

X = 0
Y = 1
NAME = 2
MOVE = 3
FRAME = 4
HEALTH = 5
MOVES = 6
PICS = 7

frame = 0
running = True
gameClock = time.Clock()
while running:
    mbd = False
    for evnt in event.get():
        if evnt.type == QUIT:
            running = False
        if evnt.type == MOUSEBUTTONDOWN:
            mbd = True
    mb = mouse.get_pressed()
    keys = key.get_pressed()
    screen.fill((255,255,255))

    if mbd and mb[0]:
        for enemy in enemies:
            doMove(enemy, 'Attack_4')
    if mbd and mb[2]:
        for enemy in enemies:
            doMove(enemy, 'Hurt')
            damage(enemy, 15)


    for enemy in enemies:
        if enemy[HEALTH] <= 0:
            kill(enemy)
        updateSprite(enemy)
        drawSprite(enemy)

    if len(enemies) < 30:
        generateEnemy()

    gameClock.tick(50)
    display.flip()
quit()