from pygame import *
from glob import *
from random import *
from math import *

screen = display.set_mode((1600,900))

def getMoves(sprite): #get all files that contain images
    moves = []
    for move in glob(f"Images/Characters/{sprite}/*"):
        moves.append(move.split('\\')[-1])
    print(moves)
    return moves

def getPics(sprite, moves): #get pictures from each file
    enemyPics = []
    for move in moves:
        movePics = []
        picNames = glob(f"Images/Characters/{sprite}/{move}/*.png")
        for picName in picNames:
            movePics.append(image.load(picName))
        enemyPics.append(movePics)
    return enemyPics

def loadItems():
    itemImages = []
    for name in glob(f"Images/drops/*.png"):
        itemPic = transform.scale(image.load(name).convert_alpha(),(32,32))
        itemImages.append(itemPic)
    return itemImages

def dropItem(position):
    item = choice(itemImages)
    droppedItems.append([item, position[0], position[1]])

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

def enemyAttack(sprite, move): # handles enemy attacks 
    current = sprite[MOVES][sprite[MOVE]] # name of current move
    damage, range, spell = attacks[sprite[NAME]][current]
    print(current, damage, range, spell)
    changeMove(sprite, move) # sets to attack move
    if sprite[FLIPPED]:
        range *= -1 # if the sprite is flipped, attack range is negative
    if spell:  # If it's a spell, apply effects to character
        hurt(sprites[0], damage)  # Hurt the player
    else:
        damage *= charDefense  # Scale damage by character's defense stat
        draw.circle(screen, (255, 0, 0), (sprite[HITBOX].centerx + range, sprite[HITBOX].centery), 10)  # Draw a red circle to indicate attack range
        if sprites[0][HITBOX].collidepoint(sprite[HITBOX].centerx + (range), sprite[HITBOX].centery) and sprites[0][HEALTH] > 0 and sprites[0][SHIELD] == False:  # Check if the sprites[0] is within range and not shielded
            hurt(sprites[0], damage)
            print('hit')

def playerAttack(sprite, move):
    current = sprite[MOVES][sprite[MOVE]] # name of current move
    damage, range, spell = attacks[sprite[NAME]][current]
    print(current, damage, range, spell)
    damage *= charDamage  if not spell else damage# Scale damage by character's damage stat
    changeMove(sprite, move) # sets to attack move
    if sprite[FLIPPED]:
        range *= -1 # if the sprite is flipped, attack range is negative
    for enemy in sprites[1:]:  # Check all enemies for collision
        draw.circle(screen, (255, 0, 0), (sprite[HITBOX].centerx + range, sprite[HITBOX].centery), 10)  # Draw a red circle to indicate attack range
        if enemy[HITBOX].collidepoint(sprite[HITBOX].centerx + (range), sprite[HITBOX].centery) and enemy[HEALTH] > 0:  # Check if the enemy is within range and not shielded
            hurt(enemy, damage)
            print('hit')

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

def movePlayer(sprite, globalx, globaly): # moves the map by x and y. Checks for walls
    x, y = 0, 0  # Initialize movement variables
    if keys[K_w] and clear(sprite[HITBOX].centerx + globalx, sprite[HITBOX].bottom + globaly - 7):
        y -= 3  # Move up by 2 pixels
    if keys[K_s] and clear(sprite[HITBOX].centerx + globalx, sprite[HITBOX].bottom + 7 + globaly):
        y += 3  # Move down by 2 pixels
    if keys[K_a] and clear(sprite[HITBOX].centerx + globalx - 20, sprite[HITBOX].bottom + globaly):
        x -= 3 # Move left by 2 pixels
        sprite[FLIPPED] = True  # Set flipped to False if moving right
    if keys[K_d] and clear(sprite[HITBOX].centerx + globalx + 20, sprite[HITBOX].bottom + globaly):
        x += 3 # Move right by 2 pixels
        sprite[FLIPPED] = False  # Set flipped to True if moving left
    global slowPlayer
    if slowPlayer:  # If the player is slowed by a spell
        if mill - start < 5000:
            x *= 0.5
            y *= 0.5
        else:
            slowPlayer = False  # Reset slow state after 2 seconds

    x *= charSpeed
    y *= charSpeed

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
    globalx += x  # Update the character's position
    globaly += y
    return globalx, globaly

def moveScene(x, y): # move every enemy baseb on player movement
    for enemy in sprites[1:]:
        enemy[HITBOX].x -= x
        enemy[HITBOX].y -= y
    for item in droppedItems:
        item[1] -= x
        item[2] -= y

def move(sprite, x, y, run=False): # moves the character (hitbox) by x and y. Sets FLIPPED flag. handles sprinting
    if x < 0:
        sprite[FLIPPED] = True
    if x > 0:
        sprite[FLIPPED] = False
    if run:
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
    changeMove(sprite, 'Hurt')  # Change to hurt move
    if sprite[HEALTH] <= 0:
        kill(sprite)
        sprite[HEALTH] = 0

def heal(sprite, amount): # increases the sprite's health by amount
    sprite[HEALTH] += amount if sprite[HEALTH] > 100 else 0  # Prevents healing above 100 health
    draw.circle(screen, (0, 255, 100), (sprite[HITBOX].centerx + randint(-15,15), sprite[HITBOX].centery + randint(-15,15)), 3)  # Draw a green circle to indicate healing

def starve(amount): # reduces the player's health if they are hungry
    pass

def kill(sprite): # removes the sprite from the enemies list
    changeMove(sprite, 'Dead')  # Change to dead before removing
    chance = [0,1,1,1,1] 
    chance = choice(chance)
    if sprite != sprites[0] and chance == 1:  # Don't drop items for player death
        dropItem(sprite[HITBOX].center)

def flipped(sprite, frame): # flips the sprite if it is facing left
    if sprite[FLIPPED]:
        return transform.flip(frame, True, False)
    return frame

def updateSprite(sprite, player=False): # updates the sprite's frame (and move for attacks)
    current = sprite[MOVES][sprite[MOVE]] # name of current move

    if player:  # If the sprite is the player, handle special cases
        if current == 'Hurt':  # If the sprite is hurt, stop updating
            sprite[FRAME] += (0.15 * charSpeed) # updates frame
            print(sprite[FRAME], current)
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                sprite[FRAME] = 0 # reset frames
                sprite[MOVE] = sprite[MOVES].index('Idle') # set them back to idle

        elif 'Attack' in current: # if they just did an attack
            sprite[FRAME] += (.25 * charSpeed) # updates frame
            if 1.8 < sprite[FRAME] < 2.1:
                playerAttack(sprite, current)  # Call player attack to handle damage
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                sprite[FRAME] = 0 # reset frames
                sprite[MOVE] = sprite[MOVES].index('Idle') # set them back to idle
        
        elif current == 'Dead':  # If the sprite is dead, stop updating
            sprite[FRAME] += 0.1  # Increment frame for dead animation
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                global running
                running = False  # If the player is dead, end the game
                sprites.remove(sprite)  # Remove the sprite from the list
                sprite[FRAME] -= .1 # Prevents frame from going out of bounds

        else: # all other moves
            sprite[FRAME] += (0.2 * charSpeed) # updates frame
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                sprite[FRAME] = 0 # reset frames
    else:
        if current == 'Hurt':  # If the sprite is hurt, stop updating
            sprite[FRAME] += 0.15 # updates frame
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                sprite[FRAME] = 0 # reset frames
                sprite[MOVE] = sprite[MOVES].index('Idle') # set them back to idle

        elif 'Attack' in current: # if they just did an attack
            sprite[FRAME] += 0.2 # updates frame
            if 2.9 < sprite[FRAME] < 3.1:
                enemyAttack(sprite, current)  # Call enemy attack to handle damage
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                sprite[FRAME] = 0 # reset frames
                sprite[MOVE] = sprite[MOVES].index('Idle') # set them back to idle

        elif current == 'Dead':  # If the sprite is dead, stop updating
            sprite[FRAME] += 0.1  # Increment frame for dead animation
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
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
    

def drawOverlay(health):
    screen.blit(fade,(-160,-90))
    screen.blit(healthBar,(1300,0))
    screen.blit(inventoryPic,(1515,115))
    if health < 200:
        draw.line(screen, (78,74,78), (1338, 16), (1338 + ((200 - health) * 0.75), 16), 15)  # Draw the health bar
    if hunger < 200:
        draw.line(screen, (78,74,78), (1338, 47), (1338 + ((200 - hunger) * 0.75), 47), 15)

def getDist(sprite1, sprite2):
    dx = sprite2[HITBOX].centerx - sprite1[HITBOX].centerx
    dy = sprite2[HITBOX].centery - sprite1[HITBOX].centery
    d = hypot(dx, dy)
    if d == 0:
        d = 1
    return d, dx, dy

def changeMain(main): # Change the player's main
    sprites[0][NAME] = main  # Change the player's name to the new main
    sprites[0][MOVES] = getMoves(main)  # Update the moves for the new main
    sprites[0][PICS] = getPics(main, sprites[0][MOVES])  # Update the pictures for the new main
    Speed, Damage, Defense = stats[main]  # Update character stats based on the new main
    return Speed, Damage, Defense

def drawInventory():
    y = 151
    for item in inventory:
        draw.rect(screen,(255,0,0),(1526,y,48,48),1)
        screen.blit(transform.scale(item,(48,48)), (1526, y))
        y += 75

def drawInventory():
    y = 151
    for item in inventory:
        draw.rect(screen,(255,0,0),(1526,y,48,48),1)
        screen.blit(transform.scale(item,(48,48)), (1526, y))
        y += 75

def openChest(chest):
    global opening
    if chest[2] == []: # if the chest is empty
        for i in range(randint(1,4)):
            chest[2].append(choice(items))  # Randomly add items to the chest
    print(chest[2])  # Print the items in the chest

#health & inventory stuff
healthBar = image.load("Images/Bars/health.png")
healthBar = transform.scale(healthBar,(300,96))
inventoryPic = image.load("Images/Bars/inventory.png")
inventoryPic = transform.scale(inventoryPic,(72,720))

# map init stuff

mask = image.load("Images/Maps/mask2.png")
mask = transform.scale(mask, (6400, 3600))  # Scale the mask to fit the screen
mask = image.load("Images/Maps/mask2.png")
mask = transform.scale(mask, (6400, 3600))  # Scale the mask to fit the screen
mapp = image.load("Images/Maps/map.png")
mapp = transform.scale(mapp, (6400, 3600)).convert()  # Scale the mask to fit the screen
fade = image.load("Images/Maps/fade.png")
WALL = (225,135,250,255)

offsetx = 0
offsety = 0

items = ['Sword', 'Potion', 'Food']  # List of items that can be found in chests
chests = [(580,130, [])]  # List to store location of chests

# Sprite init stuff
charType = 'Fighter'  # Default character type
#         name     hitbox                move frame health flipped shield
player = [charType, Rect(800,400,20,70), 5  , 0   , 200  , False, False]
#        speed, dmg, def (def is % taken)
fighter = [1.5, 0.7, 1  ]  # Fighter stats: speed, damage, defense
shinobi = [1.2, 1.2, 0.8]  # Shinobi stats: speed, damage, defense
samurai = [1  , 1.6, 0.6]  # Samurai stats: speed, damage, defense
stats = {'Fighter': fighter, 'Shinobi': shinobi, 'Samurai': samurai}  # Dictionary to hold character stats
charSpeed, charDamage, charDefense = stats[player[0]]  # Set the player's stats based on the chosen character type
player.append(getMoves(player[0]))
player.append(getPics(player[0], player[7]))
hunger = 100  # Player's hunger level

fightAttacks = {'Attack_1': (20,25, False), 'Attack_2': (15,30, False), 'Attack_3': (25,20, False)}
shinAttacks  = {'Attack_1': (20,25, False), 'Attack_2': (15,30, False), 'Attack_3': (25,20, False)}
samAttacks   = {'Attack_1': (20,25, False), 'Attack_2': (15,50, False), 'Attack_3': (25,30, False)}

#item & inventory stuff
itemImages = loadItems()      # Loads all item images
droppedItems = []             # Each is [image, x, y]
inventory = []
gold = 0  # Player's gold amount
food = 0  # Player's food amount

goldPic = image.load("Images/drops/gold.png")

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

#              move       dmg,rng
berAttacks = {'Attack_1': (15,30, False)}
shamanAttacks = {'Attack_1': (5,40, False), 'Attack_3': (10,100,True)}
warriorAttacks = {'Attack_1': (20,30, False)}

enemyTypes = [berserker, shaman, warrior]
sprites = [player]
maxEnemies = 12  # Limit the number of enemies
spawnPoints = [(400, 200), (1700, 600), (800, 1300)]  # Predefined spawn points
for point in spawnPoints:
    for i in range(4):
        generateEnemy(point)  # Generate enemies at predefined spawn points

attacks = {'berserker': berAttacks, 'shaman': shamanAttacks, 'warrior': warriorAttacks, 'Fighter':fightAttacks, 'Shinobi':shinAttacks, 'Samurai': samAttacks}  # Dictionary to hold attacks for each enemy type

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
opening = False  # Flag to indicate if a chest is being opened
gameClock = time.Clock()
while running:
    mill = time.get_ticks()  # Get the current time in milliseconds
    mbd = False
    kd = False #key down
    ku = False #key up
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
    mx, my = mouse.get_pos()

    drawScene(screen, offsetx, offsety)  # Draw the background and mask

    playerShield(sprites[0])

    offsetx, offsety = movePlayer(sprites[0], offsetx, offsety)  # Move the player character based on input

    if ku and keys[K_d] == False and keys[K_a] == False and keys[K_w] == False and keys[K_s] == False:
        stop(sprites[0])
    if kd:
        if keys[K_f]:
            charSpeed, charDamage, charDefense = changeMain('Fighter')
        if keys[K_g]:
            charSpeed, charDamage, charDefense = changeMain('Shinobi')
        if keys[K_h]:
            charSpeed, charDamage, charDefense = changeMain('Samurai')
        if keys[K_SPACE]:
            changeMove(sprites[0], 'Attack_3')
    if mbd:
        if mb[0]:
            changeMove(sprites[0], 'Attack_1')
        if mb[2]:
            changeMove(sprites[0], 'Attack_2')

    for chest in chests:  # Check for chests
        d = hypot(sprites[0][HITBOX].centerx - (chest[0] - offsetx), sprites[0][HITBOX].centery - (chest[1] - offsety))
        if d < 50 and not opening:
            print('Q to open chest')
            if keys[K_q]:
                opening = True

    if opening:  # If the chest is being opened
        openChest(chest)  # Open the chest if within range and Q is pressed

        # enemy behaviour
    for enemy in sprites[1:]:  # Skip the sprites[0]
        # print(enemy[SHIELD])
        d, dx, dy = getDist(enemy, sprites[0])

        # berseker behaviour
        if enemy[NAME] == 'berserker':
            if 0 < enemy[HEALTH] < 50: # low health
                heal(enemy, 0.1)
                if d < 100: # close to player
                    move(enemy, dx / d * -1, dy / d * -1, True)
                else:
                    stop(enemy)
            else:
                if 40 < d < 150 or -4 > dy > 4: # 40 - 150 from player. 
                    if enemy[HEALTH] > 25:
                        move(enemy, dx / d * .75, dy / d * .75)
                elif d < 40:
                    stop(enemy)  # Stop if too close
                    #         \/cooldown(milliseconds)
                    if mill % 2000 < 250:  # Attack every second
                        changeMove(enemy, 'Attack_1')
                else:
                    stop(enemy)

        # shaman behaviour
        if enemy[NAME] == 'shaman':
            if 0 < enemy[HEALTH] < 50:
                if d < 100:
                    move(enemy, dx / d * -1.5, dy / d * -1.5)
                else:
                    stop(enemy)
            elif enemy[HEALTH] > 50:
                if 40 < d < 70:
                    move(enemy, dx / d * 2, dy / d * 2)
                    if mill % 2000 < 20:
                        changeMove(enemy, 'Attack_1')
                        pass
                elif 70 < d < 150:
                    move(enemy, dx / d * -.75, dy / d * -.75)
                    move(enemy, dx / d * .05, dy / d * .05) # turn to face player
                else:
                    stop(enemy)
                if 80 < d < 160 and mill % 7000 < 20:
                    changeMove(enemy, 'Attack_3') # earthquake
                    slowPlayer = True  # Slow the player for a short duration
                    start = mill
        
        # warrior behaviour
        if enemy[NAME] == 'warrior':
            if enemy[HEALTH] > 0:
                if 70 < d < 150 or -4 > dy > 4:
                    move(enemy, dx / d * 1.5, dy / d * 1.5, True)
                elif 40 < d < 70:
                    move(enemy, dx / d, dy / d)
                elif d < 40:
                    stop(enemy)
                    if mill % 1500 < 50:
                        changeMove(enemy, 'Attack_1')
                else:
                    stop(enemy)
                
        updateSprite(enemy)

    updateSprite(sprites[0], True)
    
    # if len(sprites) < maxEnemies + 1:  # Limit the number of enemies
    #     generateEnemy(choice(spawnPoints))
    # print(sprites[0][SHIELD])
    drawOverlay(sprites[0][HEALTH])  # Draw the health bar
    drawInventory()

    for item in droppedItems:
            itempic, world_x, world_y = item
            screen.blit(itempic, (world_x, world_y))

    if mbd and mb[0]:  
        for item in droppedItems[:]:
            itempic, x, y = item
            itemRect = Rect(x,y,32,32)
            if itemRect.collidepoint(mx, my):
                inventory.append(itempic)
                droppedItems.remove(item)
    
    if time.get_ticks() % 15000 < 50:
        hunger -= 5
        print(hunger)
        if hunger < 30:
            slowPlayer = True  # Slow the player if hunger is low
        elif hunger <= 0:
            hurt(sprites[0], 10)

    gameClock.tick(50)
    # print(f'Time: {time.get_ticks()} | FPS: {gameClock.get_fps()}')  # Print FPS for debugging
    # # print(sprites[0][HITBOX].x, sprites[0][HITBOX].y)  # Print player position for debugging
    # # print(offsetx, offsety)  # Print player position for debugging
    # print(sprites[0][HEALTH])  # Print player stats
    display.flip()
quit()