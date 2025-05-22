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

def updateSprite(sprite):
    sprite[FRAME] += 0.2
    idle = sprite[MOVES].index('Idle')

    if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle
    print(sprite[MOVE], sprite[FRAME])

def doAttack(sprite, move):
    index = sprite[MOVES].index(move)
    idle = sprite[MOVES].index('Idle')
    if sprite[MOVE] == idle:
        sprite[MOVE] = index
        sprite[FRAME] = 0
    elif sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle

def drawSprite(sprite):
    pic = sprite[PICS][sprite[MOVE]][int(sprite[FRAME])]
    screen.blit(pic, (sprite[X] - pic.get_width() // 2  , sprite[Y] - pic.get_height() // 2))

NAME = 0
MOVE = 1
FRAME = 2
HEALTH = 3
MOVES = 4
PICS = 5

#            X   Y   Move          Speed
berserker = ['berserker', 5   , 0, 100]
berserker.append(getMoves(berserker[NAME]))
berserker.append(getPics(berserker[NAME], berserker[MOVES]))

shaman = ['shaman', 4   , 0, 100]
shaman.append(getMoves(shaman[NAME]))
shaman.append(getPics(shaman[NAME], shaman[MOVES]))

warrior = ['warrior', 5   , 0, 100]
warrior.append(getMoves(warrior[NAME]))
warrior.append(getPics(warrior[NAME], warrior[MOVES]))

enemyTypes = [berserker, shaman, warrior]
enemies = []
enemiesTemp = []
enemiesPos = []
for i in range(30):
    enemiesPos.append([randint(100,1100), randint(100,700)])
    enemiesTemp.append(choice(enemyTypes).copy())
for i in range(30):
    enemies.append([enemiesPos[i][0],enemiesPos[i][1], enemiesTemp[i][NAME], enemiesTemp[i][MOVE], enemiesTemp[i][FRAME], enemiesTemp[i][HEALTH], enemiesTemp[i][MOVES], enemiesTemp[i][PICS]])
    # enemies.append([randint(100,1100), randint(100,700)],choice(enemyTypes).copy())

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
    for evnt in event.get():
        if evnt.type == QUIT:
            running = False
    mb = mouse.get_pressed()
    keys = key.get_pressed()
    screen.fill((255,255,255))

    if mb[0]:
        for enemy in enemies[:15]:
            doAttack(enemy, 'Attack_1')
    if mb[2]:
        for enemy in enemies[15:]:
            doAttack(enemy, 'Attack_1')

    for enemy in enemies:
        updateSprite(enemy)
        drawSprite(enemy)

    gameClock.tick(50)
    display.flip()
quit()