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
    enemies.append([randint(100, 1100), randint(100, 700), enemyTypes[type][0], enemyTypes[type][1], enemyTypes[type][2], enemyTypes[type][3], enemyTypes[type][4], enemyTypes[type][5], enemyTypes[type][6]])

def doMove(sprite, move):
    index = sprite[MOVES].index(move)
    idle = sprite[MOVES].index('Idle')
    if sprite[MOVE] == idle:
        sprite[MOVE] = index
        sprite[FRAME] = 0
    elif sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle

def move(sprite, x, y):
    if x < 0:
        sprite[FLIPPED] = True
    if x > 0:
        sprite[FLIPPED] = False
    if keys[K_LSHIFT]:
        x *= 1.5
        y *= 1.5
        sprite[MOVE] = sprite[MOVES].index('Run')
    else:
        sprite[MOVE] = sprite[MOVES].index('Walk')
    sprite[X] += x
    sprite[Y] += y

def damage(sprite, amount):
    sprite[HEALTH] -= amount
    if sprite[HEALTH] <= 0:
        sprite[HEALTH] = 0

def kill(sprite):
    enemies.remove(sprite)

def flipped(sprite, frame):
    if sprite[FLIPPED]:
        return transform.flip(frame, True, False)
    return frame

def updateSprite(sprite):
    sprite[FRAME] += 0.2
    idle = sprite[MOVES].index('Idle')
    walk = sprite[MOVES].index('Walk')

    if sprite[MOVE] == walk and keys[K_d] == False and keys[K_a] == False and keys[K_w] == False and keys[K_s] == False:
        sprite[MOVE] = idle
        sprite[FRAME] = 0
    if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        if sprite[MOVE] != idle and sprite[MOVE] != walk:
            sprite[MOVE] = idle

def drawSprite(sprite):
    pic = sprite[PICS][sprite[MOVE]][int(sprite[FRAME])]
    screen.blit(flipped(sprite, pic), (int(sprite[X]) - pic.get_width() // 2  , int(sprite[Y]) - pic.get_height() // 2))

NAME = 0
MOVE = 1
FRAME = 2
HEALTH = 3
FLIPPED = 4
MOVES = 5
PICS = 6

player = [800, 400, 'fighter', 5, 0, 200, False]
player.append(getMoves(player[2]))
player.append(getPics(player[2], player[7]))
print(player)

#            name         move  frame health
berserker = ['berserker', 6   , 0   , 130, False]
berserker.append(getMoves(berserker[NAME]))
berserker.append(getPics(berserker[NAME], berserker[MOVES]))

shaman = ['shaman', 6   , 0, 70, False]
shaman.append(getMoves(shaman[NAME]))
shaman.append(getPics(shaman[NAME], shaman[MOVES]))

warrior = ['warrior', 6   , 0, 100, False]
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
FLIPPED = 6
MOVES = 7
PICS = 8

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

    if keys[K_d]:
        move(player, 3, 0)
    if keys[K_a]:
        move(player, -3, 0)     
    if keys[K_w]:
        move(player, 0, -3)
    if keys[K_s]:
        move(player, 0, 3)

    if keys[K_SPACE]:
        doMove(player, 'Attack_1')
    if keys[K_f]:
        doMove(player, 'Attack_2')
    if keys[K_g]:
        doMove(player, 'Attack_3')

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

    updateSprite(player)
    drawSprite(player)

    if len(enemies) < 30:
        generateEnemy()

    gameClock.tick(50)
    display.flip()
quit()