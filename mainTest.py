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

def generateEnemy(spawnPoint):
    type = randint(0, len(enemyTypes) - 1) # randomly select an enemy type
    # Create a new enemy with the selected type
    # spawnPoint = 400, 200
    x, y = spawnPoint  # Start at the spawn point
    while not clear(x, y) or (x,y) == (spawnPoint):  # Ensure the enemy is spawned in a clear area
        x += randint(-150, 150)
        y += randint(-150, 150)  # Random position for the enemy
        # print(len(sprites), x, y)
    #               name                 hitbox                                         move  frame    health       flipped  shield  moves                pics
    sprites.append([enemyTypes[type][0], Rect(x - 20, y - 60, 40, 60), 6, 0, enemyTypes[type][1], False, False,  enemyTypes[type][2], enemyTypes[type][3]])

def playerShield(sprite):
    if keys[K_LCTRL] and sprite[MOVE] == sprite[MOVES].index('Idle'):  # If CTRL is pressed and the sprite is idle
        sprite[SHIELD] = True
        changeMove(sprites[0], 'Shield')
    if sprite[SHIELD] and ku:  # If shield is active and a key is released
        sprite[SHIELD] = False
        changeMove(sprite, 'Idle')  # Change back to idle move when shield is released

def doAttack(sprite, move, damage, range, spell=False):
    current = sprite[MOVES][sprite[MOVE]] # name of current move
    if 'Attack' not in current: # if its not already attacking
        changeMove(sprite, move) # sets to attack move
        if sprite[FLIPPED]:
            range *= -1 # if the sprite is flipped, attack range is negative
        if spell:  # If it's a spell, apply effects to character
            hurt(sprites[0], damage)  # Hurt the player
        else:
            for target in sprites:
                if target[HITBOX].collidepoint(sprite[HITBOX].centerx + (range), sprite[HITBOX].centery) and target[HEALTH] > 0 and target[SHIELD] == False:  # Check if the target is within range and not shielded
                    changeMove(target, 'Hurt')
                    hurt(target, damage)
                    print('hit')
    sprite[SHIELD] = False  # Reset shield state when attacking

def changeMove(sprite, move): # changes the sprite's move to the specified move, resets frame if it was idle
    if sprite[MOVE] != sprite[MOVES].index('Dead') and sprite[MOVE] != sprite[MOVES].index(move):  # If not already dead or the same move
        index = sprite[MOVES].index(move) # gets the index of the move
        sprite[MOVE] = index # sets the move to the index of the move
        sprite[FRAME] = 0 # resets the frame

def clear(maskX, maskY): # checks if the pixel at maskX, maskY is clear (not a wall)
    if maskX < 0 or maskX >= mask.get_width() or maskY < 0 or maskY >= mask.get_height():
        return False
    else:
        return mask.get_at((int(maskX), int(maskY))) != WALL

def movePlayer(sprite, X, Y): # moves the map by x and y. Checks for walls
    x, y = 0, 0  # Initialize movement variables
    if keys[K_w] and clear(sprite[HITBOX].centerx + X, sprite[HITBOX].bottom + Y - 7):
        y -= 2  # Move up by 2 pixels
    if keys[K_s] and clear(sprite[HITBOX].centerx + X, sprite[HITBOX].bottom + 7 + Y):
        y += 2  # Move down by 2 pixels
    if keys[K_a] and clear(sprite[HITBOX].centerx + X - 7, sprite[HITBOX].bottom + Y):
        x -= 2 # Move left by 2 pixels
        sprite[FLIPPED] = True  # Set flipped to False if moving right
    if keys[K_d] and clear(sprite[HITBOX].centerx + X + 7, sprite[HITBOX].bottom + Y):
        x += 2 # Move right by 2 pixels
        sprite[FLIPPED] = False  # Set flipped to True if moving left
    global slowPlayer, start
    if slowPlayer:  # If the player is slowed by a spell
        if mill - start < 2000:
            x *= 0.5
            y *= 0.5
        else:
            slowPlayer = False  # Reset slow state after 2 seconds

    if x == 0 and y == 0:  # If no movement keys are pressed
        stop(sprite)
    elif keys[K_LSHIFT]:  # If sprinting, increase speed
        x *= 1.5
        y *= 1.5
        changeMove(sprite, 'Run')
    else:
        changeMove(sprite, 'Walk')
    x = int(x)  # Convert to integer for pixel movement
    y = int(y)
    moveScene(x, y)
    X += x  # Update the character's position
    Y += y
    return X, Y

def moveScene(x, y):
    for enemy in sprites[1:]:
        enemy[HITBOX].x -= x
        enemy[HITBOX].y -= y
    return x, y

def move(sprite, x, y): # moves the character (hitbox) by x and y. Sets FLIPPED flag. handles sprinting
    if x < 0:
        sprite[FLIPPED] = True
    if x > 0:
        sprite[FLIPPED] = False
    if keys[K_LSHIFT]:
        x *= 1.5 # increase speed if sprinting
        y *= 1.5
        changeMove(sprite, 'Run') # sets the move to run
    else:
        changeMove(sprite, 'Walk') # sets the move to walk
    # Check for walls before moving
    if clear(sprite[HITBOX].centerx + x + offsetx, sprite[HITBOX].bottom + y + offsety):
        sprite[HITBOX].x += x
        sprite[HITBOX].y += y
    sprite[SHIELD] = False  # Reset shield state when moving

def stop(sprite): # just sets the sprite to idle if it was moving
    if sprite[MOVE] == sprite[MOVES].index('Walk') or sprite[MOVE] == sprite[MOVES].index('Run'):
        sprite[MOVE] = sprite[MOVES].index('Idle')

def hurt(sprite, amount): # reduces the sprite's health by amount
    sprite[HEALTH] -= amount
    if sprite[HEALTH] <= 0:
        kill(sprite)

def heal(sprite, amount): # increases the sprite's health by amount
    sprite[HEALTH] += amount if sprite[HEALTH] > 100 else 0  # Prevents healing above 100 health
    draw.circle(screen, (0, 255, 100), (sprite[HITBOX].centerx + randint(-15,15), sprite[HITBOX].centery + randint(-15,15)), 3)  # Draw a green circle to indicate healing

def kill(sprite): # removes the sprite from the enemies list
    changeMove(sprite, 'Dead')  # Change to dead before removing

def flipped(sprite, frame): # flips the sprite if it is facing left
    if sprite[FLIPPED]:
        return transform.flip(frame, True, False)
    return frame

def updateSprite(sprite): # updates the sprite's frame (and move for attacks)
    current = sprite[MOVES][sprite[MOVE]] # name of current move

    if 'Attack' in current or current == 'Hurt': # if they just did an attack
        sprite[FRAME] += 0.25 # updates frame
        if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
            sprite[FRAME] = 0 # reset frames
            sprite[MOVE] = sprite[MOVES].index('Idle') # set them back to idle

    elif current == 'Dead':  # If the sprite is dead, stop updating
        sprite[FRAME] += 0.1  # Increment frame for dead animation
        if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
            if sprite == sprites[0]:
                global running
                running = False  # If the player is dead, end the game
            sprites.remove(sprite)  # Remove the sprite from the list
            sprite[FRAME] -= .1 # Prevents frame from going out of bounds

    else: # all other moves
        sprite[FRAME] += 0.2 # updates frame
        if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
            sprite[FRAME] = 0 # reset frames

    drawSprite(sprite)

def drawSprite(sprite):
    pic = sprite[PICS][sprite[MOVE]][int(sprite[FRAME])]
    draw.rect(screen, (0,0,0), sprite[HITBOX], 1)  # Draw hitbox for debugging
    screen.blit(flipped(sprite, pic), (sprite[HITBOX].centerx - pic.get_width() // 2, sprite[HITBOX].centery - pic.get_height() // 2))

def drawScene(screen, x, y):
    ''' As always, ALL drawing happens here '''
    screen.blit(mapp, (-x, -y))

def getDist(sprite1, sprite2):
    dx = sprite2[HITBOX].centerx - sprite1[HITBOX].centerx
    dy = sprite2[HITBOX].centery - sprite1[HITBOX].centery
    d = hypot(dx, dy)
    if d == 0:
        d = 1
    return d, dx, dy

#health & inventory stuff
health = image.load("Images/Bars/health.png")
health = transform.scale(health,(300,96))
inventory = image.load("Images/Bars/inventory.png")

# map init stuff

mask = image.load("Images/Maps/mask2.png")
mask = transform.scale(mask, (6400, 3600))  # Scale the mask to fit the screen
mask = image.load("Images/Maps/mask2.png")
mask = transform.scale(mask, (6400, 3600))  # Scale the mask to fit the screen
mapp = image.load("Images/Maps/map.png")
mapp = transform.scale(mapp, (6400, 3600)).convert()  # Scale the mask to fit the screen
WALL = (225,135,250,255)

offsetx = 0
offsety = 0

# Sprite init stuff
#         name     hitbox                move frame health flipped shield
player = ['Shinobi', Rect(800,400,20,70), 5  , 0   , 200  , False, False]
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
sprites = [player]
maxEnemies = 12  # Limit the number of enemies
spawnPoints = [(400, 200), (1700, 600), (800, 1300)]  # Predefined spawn points
for point in spawnPoints:
    for i in range(4):
        generateEnemy(point)  # Generate enemies at predefined spawn points

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
slowPlayer = False
gameClock = time.Clock()
while running:
    mill = time.get_ticks()  # Get the current time in milliseconds
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
    screen.fill(0)
    drawScene(screen, offsetx, offsety)  # Draw the background and mask

    playerShield(sprites[0])

    offsetx, offsety = movePlayer(sprites[0], offsetx, offsety)  # Move the player character based on input

    if ku and keys[K_d] == False and keys[K_a] == False and keys[K_w] == False and keys[K_s] == False:
        stop(sprites[0])

    if kd:
        if keys[K_SPACE]:
            doAttack(sprites[0], 'Attack_3', 25, 20)

    if mbd:
        if mb[0]:
            doAttack(sprites[0], 'Attack_1', 15, 25)
        if mb[2]:
            doAttack(sprites[0], 'Attack_2', 15, 25)


    # enemy behaviour
    for enemy in sprites[1:]:  # Skip the sprites[0]
        # print(enemy[SHIELD])
        d, dx, dy = getDist(enemy, sprites[0])

        # berseker behaviour
        if enemy[NAME] == 'berserker':
            if 0 < enemy[HEALTH] < 50: # low health
                heal(enemy, 0.01)
                if d < 100: # close to player
                    move(enemy, dx / d * -1.5, dy / d * -1.5)
                else:
                    stop(enemy)
            else:
                if 40 < d < 150 or -2 > dy > 2: # 40 - 150 from player. 
                    if enemy[HEALTH] > 25:
                        move(enemy, dx / d * 1.5, dy / d * 1.5)
                elif d < 40:
                    #         \/cooldown(milliseconds)
                    if mill % 2000 < 250:  # Attack every second
                        doAttack(enemy, 'Attack_1', 15, 30)
                else:
                    
                    stop(enemy)

        # shaman behaviour
        if enemy[NAME] == 'shaman':
            if 0 < enemy[HEALTH] < 50:
                if d < 100:
                    move(enemy, dx / d * -1.5, dy / d * -1.5)
                else:
                    stop(enemy)
            else:
                if d < 50 and mill % 2000 < 250:
                    doAttack(enemy, 'Attack_1', 5, 40)
                if d < 150 and mill % 5000 < 250:
                    doAttack(enemy, 'Attack_3', 10, 100, True) # earthquake
                    slowPlayer = True  # Slow the player for a short duration
                    start = mill
                    
                
        updateSprite(enemy)

    updateSprite(sprites[0])
    
    # if len(sprites) < maxEnemies + 1:  # Limit the number of enemies
    #     generateEnemy(choice(spawnPoints))
    # print(sprites[0][SHIELD])

    screen.blit(health,(1300,0))

    gameClock.tick(50)
    print(f'Time: {time.get_ticks()} | FPS: {gameClock.get_fps()}')  # Print FPS for debugging
    # print(sprites[0][HITBOX].x, sprites[0][HITBOX].y)  # Print player position for debugging
    # print(offsetx, offsety)  # Print player position for debugging
    print(sprites[0][HEALTH])  # Print player stats
    display.flip()
quit()