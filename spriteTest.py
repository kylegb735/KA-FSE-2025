from pygame import *
from glob import *

screen = display.set_mode((1200,800))

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
    print(enemyPics)
    return enemyPics

def update(sprite, move):
    keys = key.get_pressed()
    mb = mouse.get_pressed()
    index = sprite[MOVES].index(move)
    idle = sprite[MOVES].index('Idle')
    sprite[FRAME] += 0.2
    if sprite[MOVE] == idle:
        if mb[0]:
            sprite[MOVE] = index
            sprite[FRAME] = 0
        else:
            sprite[MOVE] = idle
    elif sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle

    if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
    print(sprite[MOVE], sprite[FRAME])

def drawSprite(sprite):
    pic = sprite[PICS][sprite[MOVE]][int(sprite[FRAME])]
    screen.blit(pic, (sprite[X] + pic.get_width() // 2  , sprite[Y] + pic.get_height() // 2))

X = 0
Y = 1
NAME = 2
MOVE = 3
FRAME = 4
MOVES = 5
PICS = 6

#        X   Y   Move  Speed
# berserkerMoves = ['Idle', 'Attack_1', 'Attack_2', 'Attack_3', 'Dead', 'Hurt', 'Jump', 'Run', 'Run+Attack', 'Walk']
berserker = [600,400, 'berserker', 5   , 0]
berserker.append(getMoves(berserker[NAME]))
berserker.append(getPics(berserker[NAME], berserker[MOVES]))

shaman = [400,400, 'shaman', 4   , 0]
shaman.append(getMoves(shaman[NAME]))
shaman.append(getPics(shaman[NAME], shaman[MOVES]))

enemies = [berserker, shaman]

frame = 0
running = True
gameClock = time.Clock()
while running:
    for evnt in event.get():
        if evnt.type == QUIT:
            running = False
    screen.fill((255,255,255))
    for enemy in enemies:
        update(enemy, 'Attack_1')
        drawSprite(enemy)
    
    gameClock.tick(50)
    display.flip()
quit()