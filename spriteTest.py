from pygame import *
from glob import *
from random import *
from math import *

screen = display.set_mode((1600,900))

def getMoves(sprite): 
    moves = []
    for move in glob(f"Images/Characters/{sprite}/*"):
        moves.append(move.split('\\')[-1])
    print(moves)
    return moves

def getPics(sprite, moves):
    enemyPics = []
    for move in moves:
        movePics = []
        picNames = glob(f"Images/Characters/{sprite}/{move}/*.png")
        for picName in picNames:
            movePics.append(image.load(picName))
        enemyPics.append(movePics)
    return enemyPics

def generateEnemy():
    type = randint(0, len(enemyTypes) - 1) # randomly select an enemy type
    # Create a new enemy with the selected type
    #               name                 hitbox                                         move  frame    health       flipped  shield  moves                pics
    enemies.append([enemyTypes[type][0], Rect(randint(100,1500),randint(100,800), 40, 60), 6, 0, enemyTypes[type][1], False, False,  enemyTypes[type][2], enemyTypes[type][3]])

def doAttack(sprite, move, damage, range):
    current = sprite[MOVES][sprite[MOVE]]
    if 'Attack' not in current:
        changeMove(sprite, move)
        if not sprite[FLIPPED]:
            flipped = 1
        else:
            flipped = -1
        for enemy in enemies:
            if enemy[HITBOX].collidepoint(sprite[HITBOX].centerx + (range * flipped), sprite[HITBOX].centery):
                changeMove(enemy, 'Hurt')
                hurt(enemy, damage)
    sprite[SHIELD] = False  # Reset shield state when attacking

def changeMove(sprite, move):
    index = sprite[MOVES].index(move)
    idle = sprite[MOVES].index('Idle')
    if sprite[MOVE] == idle:
        sprite[MOVE] = index
        sprite[FRAME] = 0
    elif sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0
        sprite[MOVE] = idle

def move(sprite, x, y): # moves the character by x and y. Sets FLIPPED flag. handles sprinting
    if x < 0:
        sprite[FLIPPED] = True
    if x > 0:
        sprite[FLIPPED] = False
    if keys[K_LSHIFT]:
        x *= 1.5 # increase speed if sprinting
        y *= 1.5
        sprite[MOVE] = sprite[MOVES].index('Run')
    else:
        sprite[MOVE] = sprite[MOVES].index('Walk')
    sprite[HITBOX].x += x
    sprite[HITBOX].y += y
    sprite[SHIELD] = False  # Reset shield state when moving

def stop(sprite): # just sets the sprite to idle if it was moving
    if sprite[MOVE] == sprite[MOVES].index('Walk') or sprite[MOVE] == sprite[MOVES].index('Run'):
        sprite[MOVE] = sprite[MOVES].index('Idle')

def hurt(sprite, amount): # reduces the sprite's health by amount
    sprite[HEALTH] -= amount
    if sprite[HEALTH] <= 0:
        sprite[HEALTH] = 0

def kill(sprite): # removes the sprite from the enemies list
    enemies.remove(sprite)

def flipped(sprite, frame): # flips the sprite if it is facing left
    if sprite[FLIPPED]:
        return transform.flip(frame, True, False)
    return frame

def updateSprite(sprite): # updates the sprite's frame (and move for attacks)
    sprite[FRAME] += 0.2 # updates frame
    idle = sprite[MOVES].index('Idle') # index of idle move
    current = sprite[MOVES][sprite[MOVE]] # name of current move
    if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
        sprite[FRAME] = 0 # reset frames
        if 'Attack' in current: # if they just did an attack
            sprite[MOVE] = idle # set them back to idle
    
def drawSprite(sprite):
    pic = sprite[PICS][sprite[MOVE]][int(sprite[FRAME])]
    draw.rect(screen, (0,0,0), sprite[HITBOX], 1)  # Draw hitbox for debugging
    screen.blit(flipped(sprite, pic), (sprite[HITBOX].centerx - pic.get_width() // 2  , sprite[HITBOX].centery - pic.get_height() // 2))

def getDist(sprite1, sprite2):
    dx = sprite2[HITBOX].centerx - sprite1[HITBOX].centerx
    dy = sprite2[HITBOX].centery - sprite1[HITBOX].centery
    d = hypot(dx, dy)
    if d == 0:
        d = 1
    return d, dx, dy

#         name     hitbox                move frame health flipped shield
player = ['Fighter', Rect(800,400,20,70), 5  , 0   , 200  , False, False]
player.append(getMoves(player[0]))
player.append(getPics(player[0], player[7]))

NAME = 0
HEALTH = 1
MOVES = 2

#            name         move  frame health
berserker = ['berserker', 130]
berserker.append(getMoves(berserker[NAME]))
berserker.append(getPics(berserker[NAME], berserker[MOVES]))

shaman = ['shaman', 70]
shaman.append(getMoves(shaman[NAME]))
shaman.append(getPics(shaman[NAME], shaman[MOVES]))

warrior = ['warrior', 100]
warrior.append(getMoves(warrior[NAME]))
warrior.append(getPics(warrior[NAME], warrior[MOVES]))

enemyTypes = [berserker, shaman, warrior]
enemies = []
for i in range(30):
    generateEnemy()

sprites = [player, enemies]



NAME = 0
HITBOX = 1
MOVE = 2
FRAME = 3
HEALTH = 4
FLIPPED = 5
SHIELD = 6
MOVES = 7
PICS = 8

frame = 0
running = True
gameClock = time.Clock()
while running:
    mbd = False
    kd = False
    ku = False
    for evnt in event.get():
        if evnt.type == QUIT:
            running = False
        if evnt.type == MOUSEBUTTONDOWN:
            mbd = True
        if evnt.type == KEYDOWN:
            kd = True
        if evnt.type == KEYUP:
            ku = True
    mb = mouse.get_pressed()
    keys = key.get_pressed()
    screen.fill((255,255,255))

    if keys[K_LCTRL]:
        player[SHIELD] = True
    if keys[K_d]:
        move(player, 3, 0)
    if keys[K_a]:
        move(player, -3, 0)     
    if keys[K_w]:
        move(player, 0, -3)
    if keys[K_s]:
        move(player, 0, 3)

    if ku and keys[K_d] == False and keys[K_a] == False and keys[K_w] == False and keys[K_s] == False:
        stop(player)

    if kd:
        if keys[K_SPACE]:
            doAttack(player, 'Attack_3', 25, 20)

    if mbd:
        if mb[0]:
            doAttack(player, 'Attack_1', 15, 25)
        if mb[2]:
            doAttack(player, 'Attack_2', 15, 25)

    if player[SHIELD]:
        changeMove(player, 'Shield')

    for enemy in enemies:
        d, dx, dy = getDist(enemy, player)
        if 40 < d < 150:
            if enemy[HEALTH] > 25:
                move(enemy, dx / d * 2, dy / d * 2)
            else:
                move(enemy, dx / d * 2, dy / d * 2)
        else:
            stop(enemy)

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