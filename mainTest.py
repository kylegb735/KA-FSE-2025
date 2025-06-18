from pygame import *
from glob import *
from random import *
from math import *

screen = display.set_mode((1600,900))
init()
introfont = font.SysFont("Georgia",36)

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
    x -= offsetx  # Adjust for the current offset
    y -= offsety  # Adjust for the current offset
    #               name                 hitbox                              move                 frame health       flipped  shield  moves                pics
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
    if bossWall and BOSSWALL.collidepoint(maskX, maskY):
        return False
    if maskX < 0 or maskX >= mask.get_width() or maskY < 0 or maskY >= mask.get_height():
        return False
    else:
        return mask.get_at((int(maskX), int(maskY))) != WALL

def movePlayer(sprite, globalx, globaly): # moves the map by x and y. Checks for walls
    x, y = 0, 0  # Initialize movement variables
    if keys[K_w] and clear(sprite[HITBOX].centerx + globalx, sprite[HITBOX].bottom + globaly - 14):
        y -= 5  # Move up by 2 pixels
    if keys[K_s] and clear(sprite[HITBOX].centerx + globalx, sprite[HITBOX].bottom + 14 + globaly):
        y += 5  # Move down by 2 pixels
    if keys[K_a] and clear(sprite[HITBOX].centerx + globalx - 30, sprite[HITBOX].bottom + globaly):
        x -= 5 # Move left by 2 pixels
        sprite[FLIPPED] = True  # Set flipped to False if moving right
    if keys[K_d] and clear(sprite[HITBOX].centerx + globalx + 30, sprite[HITBOX].bottom + globaly):
        x += 5 # Move right by 2 pixels
        sprite[FLIPPED] = False  # Set flipped to True if moving left
    global slowPlayer
    if slowPlayer:  # If the player is slowed by a spell
        if mill - spellStart < 7000:
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
    if sprite[MOVE] == sprite[MOVES].index('Walk'):
        sprite[MOVE] = sprite[MOVES].index('Idle')
    if 'Run' in sprite[MOVES]:
        if sprite[MOVE] == sprite[MOVES].index('Run'):
            sprite[MOVE] = sprite[MOVES].index('Idle')

def hurt(sprite, amount): # reduces the sprite's health by amount
    sprite[HEALTH] -= amount
    if not (sprite[NAME] == 'Boss' and sprite[MOVE] == sprite[MOVES].index('Attack')):  # If not the boss and not already hurt
        changeMove(sprite, 'Hurt')  # Change to hurt move
    if sprite[HEALTH] <= 0:
        kill(sprite)
        sprite[HEALTH] = 0

def heal(sprite, amount): # increases the sprite's health by amount
    sprite[HEALTH] += amount if sprite[HEALTH] > 100 else 0  # Prevents healing above 100 health
    draw.circle(screen, (0, 255, 100), (sprite[HITBOX].centerx + randint(-15,15), sprite[HITBOX].centery + randint(-15,15)), 3)  # Draw a green circle to indicate healing

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

    if player == 'player':  # If the sprite is the player, handle special cases
        if current == 'Hurt':  # If the sprite is hurt, stop updating
            sprite[FRAME] += (0.15 * charSpeed) # updates frame
            print(sprite[FRAME], current)
            if sprite[FRAME] >= len(sprite[PICS][sprite[MOVE]]):
                sprite[FRAME] = 0 # reset frames
                sprite[MOVE] = sprite[MOVES].index('Idle') # set them back to idle

        elif 'Attack' in current: # if they just did an attack
            sprite[FRAME] += (.25 * charSpeed) # updates frame
            if 1.8 < sprite[FRAME] < 2.5:
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
    elif player == 'boss':
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
                running = False  # If the player is dead, end the game
                sprites.remove(sprite)  # Remove the sprite from the list
                sprite[FRAME] -= .1 # Prevents frame from going out of bounds

        else: # all other moves
            sprite[FRAME] += 0.2 # updates frame
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
    if bossWall:
        screen.blit(wall,(3750-x,700-y))

def drawOverlay(health):
    screen.blit(fade,(-160,-90))
    screen.blit(healthBar,(1300,0))
    screen.blit(inventoryPic,(1515,115))
    screen.blit(transform.scale(goldPic,(48,48)), (1526, 152))  # Draw the gold icon
    goldText = font.SysFont("Georgia", 20).render(f"{str(gold)}", True, (255, 255, 0))
    screen.blit(goldText, (1578, 160))
    if weaponPic != 'None':  # If a weapon is equipped
        screen.blit(transform.scale(weaponPic, (45,45)), (1529, 24))  # Draw the weapon icon
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
    weaponPic = weapons[main] if main in weapons else 'None'  # Get the weapon picture for the new main
    Speed, Damage, Defense = stats[main]  # Update character stats based on the new main
    return Speed, Damage, Defense, weaponPic

def drawInventory():
    y = 225
    i = 0
    print(covers)
    for item in inventory:
        screen.blit(transform.scale(item,(48,48)), (1526, y))
        print(covers[i], i)
        if covers[i] != None:
            screen.blit(covers[i], (1526, y + (51 - covers[i].get_height())))
        i += 1
        y += 75

def openChest(currentchest):  
    global activeLoreItem, showLore, gold, bossWall
    screen.blit(insidechest,(1250,439))
    chestinventory = currentchest[2]

    x = 1261
    y = 451
    
    for item in chestinventory[:5]:
            screen.blit(transform.scale(item,(48,48)), (x, y))
            itemRect = Rect(x, y, 48, 48)
            if mbd and mb[0] and itemRect.collidepoint(mx, my) and len(inventory) < 8:
                inventory.append(item)
                chestinventory.remove(item)
                if item in itemLore:
                    activeLoreItem = item
                    showLore = True
            y += 75

    for item in chestinventory[5:10]:
        screen.blit(transform.scale(item,(48,48)), (x + 75, y - 375))
        itemRect = Rect(x + 75, y - 375, 48, 48)
        if mbd and mb[0] and itemRect.collidepoint(mx, my) and len(inventory) < 8:
            inventory.append(item)
            chestinventory.remove(item)
            if item in itemLore:
                activeLoreItem = item
                showLore = True
        y += 75
    
    for item in chestinventory[10:14]:
        screen.blit(transform.scale(item,(48,48)), (x + 149, y - 750))
        itemRect = Rect(x + 149, y - 750, 48, 48)
        if mbd and mb[0] and itemRect.collidepoint(mx, my) and len(inventory) < 8:
            inventory.append(item)
            chestinventory.remove(item)
            if item in itemLore:
                activeLoreItem = item
                showLore = True
        y += 75
        
    if currentchest[3] == 1:
        y = 225
        screen.blit(insidechest,(1250,439))
        for item in inventory:
                itemRect = Rect(1526, y, 48, 48)
                if mbd and mb[0] and itemRect.collidepoint(mx, my):  
                    if item in itemLore:
                            currentchest[2].append(item)
                            inventory.remove(item)
                            if all(i in chestinventory for i in [claw, book, puppet, scale, horn, crown]):
                                bossWall = False
                    else:
                        inventory.remove(item)
                        global gold
                        gold += 10
                y += 75
    else:
        y = 225
        for item in inventory:
                itemRect = Rect(1526, y, 48, 48)
                if mbd and mb[0] and itemRect.collidepoint(mx, my) and len(chestinventory) < 15:  
                    chestinventory.append(item)
                    inventory.remove(item)
                y += 75

def eat(pos):
    global eatStart, eating, foodCover, hunger
    if hunger < 200 and foodPic in inventory:
        if kd:
            eatStart = mill  # Start eating when the key is pressed
            eating = True  # Set eating flag to True
        foodCover = makeCover(eatStart)  # Create a surface for the food cover
        covers[pos] = foodCover  # Add the food cover to the covers list
        if mill - eatStart > 2000:
            eating = False  # Reset eating flag after 2 seconds
            hunger += 65
            inventory.remove(foodPic)  # Remove the food from inventory after eating
            eatStart = mill

def makeCover(start):
    foodCover = Surface((49, 51))  # Create a surface for the food cover
    foodCover.fill((0, 0, 0, 0))
    foodCover.set_colorkey((0, 0, 0))
    foodCover.set_alpha(200)
    draw.rect(foodCover, (111, 111, 111), (0, (0 + (mill - start) / 2000 * 49), 49, 51 - (mill - start) / 2000 * 49))
    return foodCover  # Return the food cover surface

#health & inventory stuff
healthBar = image.load("Images/Bars/health.png")
healthBar = transform.scale(healthBar,(300,96))
inventoryPic = image.load("Images/Bars/inventory.png")
inventoryPic = transform.scale(inventoryPic,(72,720))
insidechest = transform.scale(image.load("Images/Bars/chest.png"),(219,372))

# map init stuff

mask = image.load("Images/Maps/mask3.png")
mask = transform.scale(mask, (6400, 3600))  # Scale the mask to fit the screen
mapp = image.load("Images/Maps/map2.png")
mapp = transform.scale(mapp, (6400, 3600)).convert()  # Scale the mask to fit the screen
wall = transform.scale(image.load("Images/Maps/wall.png"),(128,128))
fade = image.load("Images/Maps/fade.png")
WALL = (225,135,250,255)
BOSSWALL = Rect(3750, 736, 216, 14)
bossWall = True
covers = []  # List to hold cover surfaces for eating
for i in range(9):
    covers.append(None)

#buttons
startbut = image.load("Images/buttons/start3.png")
scorebut = image.load("Images/buttons/score3.png")


#title
title = image.load("Images/Maps/name.png")
title = transform.scale(title, (936, 880))  


offsetx, offsety = 0,0

# Sprite init stuff
charType = 'Fighter'  # Default character type
#         name     hitbox                move frame health flipped shield
player = [charType, Rect(800,400,20,70), 5  , 0   , 200  , False, False]

#        speed, dmg, def (def is % taken)
fighter = [1.2, 0.7, 1  ]  # Fighter stats: speed, damage, defense
shinobi = [1.2, 1.2, 0.8]  # Shinobi stats: speed, damage, defense
samurai = [1  , 1.6, 0.6]  # Samurai stats: speed, damage, defense
stats = {'Fighter': fighter, 'Shinobi': shinobi, 'Samurai': samurai}  # Dictionary to hold character stats
charSpeed, charDamage, charDefense = stats[player[0]]  # Set the player's stats based on the chosen character type
player.append(getMoves(player[0]))
player.append(getPics(player[0], player[7]))
hunger = 100  # Player's hunger level
#                           dmg rng spell
fightAttacks = {'Attack_1': (15,25, False), 'Attack_2': (10,30, False), 'Attack_3': (20,20, False)}
shinAttacks  = {'Attack_1': (20,25, False), 'Attack_2': (15,30, False), 'Attack_3': (25,20, False)}
samAttacks   = {'Attack_1': (25,35, False), 'Attack_2': (20,50, False), 'Attack_3': (35,30, False)}

#item & inventory stuff
itemImages = loadItems()      # Loads all item images
droppedItems = []             # Each is [image, x, y]


gold = 0  # Player's gold amount
food = 0  # Player's food amount
goldPic = image.load("Images/drops/gold.png")
foodPic = image.load("Images/drops/food.png")
claw = image.load("Images/Collectables/Dragons Claw.png")
book = image.load("Images/Collectables/Book of Skulls.png")
puppet = image.load("Images/Collectables/Cursed Puppet.png")
scale = image.load("Images/Collectables/Drogmirs Scales.png")
horn = image.load("Images/Collectables/Hollows Horn.png")
crown = image.load("Images/Collectables/Old Kings Crown.png")
inventory = [foodPic]

itemLore = {
    claw:  ["~The Dragon's Claw~","Ripped from Drogmir the Dragons corpse.","Said to still twitch with cursed heat.","Indestructible"],
    book:  ["~The Book of Skulls~","Contains the names of those sacrificed to the Hollow King.",
            "The last page has symbols that have never been translated, but rumors say it has his true name.","Indestructible "],
    puppet:["~The Cursed Puppet~","A tool used by traitors to manipulate the minds of the pure.","Unknown origins.",
            "Rumored to belong to the Hollow King.","Destructable- damaging it leads to instant death (63 dead)"],
    scale: ["~Drogmir's Scale~","Legends say it blocked the Hollow King's blade.","Emanates ancient, forgotten magic","Indestructible"],
    horn:  ["~The Hollow’s Horn~","The Hollow Kings fathers horn.","Taken from his dead body","Blown only at the beginning of Velmara’s fall."],
    crown: ["~The Old King’s Crown~","Oldest Velmarian artifact, passed on from the first Velmarian king", "Lost in the final battle before Velmara’s fall to shadow."]
}
weapons = {'Shinobi': transform.scale(image.load("Images/Weapons/Dagger.png").convert_alpha(), (32, 32)), 'Samurai': transform.scale(image.load("Images/Weapons/Katana.png").convert_alpha(), (32, 32))}  # Dictionary to hold weapon images
weaponPic = 'None'  # Default weapon
chests = [
    (560,130, [weapons['Samurai']] + [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))], 0),
    (1764,2440,[claw]+ [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))],0),
    (1402,1748,[puppet]+ [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))],0),
    (2812,554,[scale]+ [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))],0),
    (2452,2772,[horn]+ [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))],0),
    (2208,3252,[crown]+ [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))],0),
    (4412,2474,[book]+ [choice(itemImages) for i in range(randint(3,5))] + [foodPic for i in range(randint(0,3))],0),
    (5792,2505,[],1)
    ]  # List to store location of chests

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

#         name     hitbox             move frame health flipped shield
boss = ['Boss', Rect(5500, 500, 40, 110), 3 , 0   , 750  , False, False]
boss.append(getMoves(boss[0]))
boss.append(getPics(boss[0], boss[7]))

bossAttacks = {'Attack': (65, 45, False)}

sprites = [player, boss]
maxEnemies = 12  # Limit the number of enemies
spawnPoints = [ (1700, 600), (800, 1300)]  # Predefined spawn points
for point in spawnPoints:
    for i in range(4):
        generateEnemy(point)  # Generate enemies at predefined spawn points

attacks = {'berserker': berAttacks, 'shaman': shamanAttacks, 'warrior': warriorAttacks, 'Fighter':fightAttacks, 'Shinobi':shinAttacks, 'Samurai': samAttacks, 'Boss': bossAttacks}  # Dictionary to hold attacks for each enemy type

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
start = False
transition = True
startRect = Rect(1263,409,320,50)
scoreRect = Rect(1346,758,234,122)
running = True
eating = False  # Flag to indicate if the player is eating
slowPlayer = False
opening = False  # Flag to indicate if a chest is being opened
bossFight = False
fight = 0
respawning = False
gameClock = time.Clock()
showLore = False
activeLoreItem = None

"""
introtext = [
        "Centuries ago...",
        "The Mad King Minos waged a terrible war",
        "The Kingdom of Velmara fell to shadows...",
        "With her last breath, Princess Rose damned the Mad King",
        "Now he sits on a cursed throne , feeding on souls.",
        "You are the last hope—",
        "The last of Velmarian blood.",
        "Enter the castle!",
        "Restore peace!",
        "Free the tortured souls",
        "Or die trying...",
        ]
    
for a in range(40):
    introtextcover = Surface((1600,900))
    introtextcover.fill(0)
    introtextcover.set_alpha(a)
    for i, line in enumerate(introtext):
            introtxt = introfont.render(line, True, (215, 166, 83))
            introtextcover.blit(introtxt, (100, 40 + i * 80))
    screen.blit(introtextcover,(0,0))
    display.flip()
    time.wait(20)

waiting = True

while waiting:
    for evnt in event.get():
        if evnt.type == QUIT:
            quit()
        if evnt.type == MOUSEBUTTONDOWN and evnt.button == 1:
            waiting = False

    for i, line in enumerate(introtext):
        introtxt = introfont.render(line, True, (215, 166, 83))
        introtextcover.blit(introtxt, (100, 40 + i * 80))

    time.wait(100)
    screen.blit(introfont.render("Click to continue", True, (215, 166, 83)), (1325, 850))
    display.flip()
    time.wait(30)

screen.fill(0)

for a in range(40):
    print(a)
    introtextcover = Surface((1600,900))
    introtextcover.fill(0)
    introtextcover.set_alpha(a)
    introtextcover.blit(font.SysFont("Georgia",64).render("Welcome", True, (215, 166, 83)), (655, 335))
    introtextcover.blit(font.SysFont("Georgia",64).render("To", True, (215, 166, 83)), (760, 405))
    introtextcover.blit(font.SysFont("Georgia",64).render("The", True, (215, 166, 83)), (740, 475))
    screen.blit(introtextcover,(0,0))
    display.flip()
    time.wait(20)

for a in range(50):
    titlecover = Surface((1600,900))
    titlecover.fill(0)
    titlecover.set_alpha(a)
    titlecover.blit(title,(332,9))
    screen.blit(titlecover,(0,0))
    display.flip()
    time.wait(20)

waiting = True

while waiting:
    for evnt in event.get():
        if evnt.type == QUIT:
            quit()
        if evnt.type == MOUSEBUTTONDOWN and evnt.button == 1:
            waiting = False

    screen.fill((0, 0, 0))
    screen.blit(title, (332, 9))
    screen.blit(introfont.render("Click to continue", True, (215, 166, 83)), (1325, 850))
    display.flip()
    time.wait(30)
"""
while running:
    mill = time.get_ticks()  # Get the current time in milliseconds
    mbd = False
    kd = False #key down
    ku = False #key up
    qd = False
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
    mx, my = mouse.get_pos()

    if not start:
        screen.fill(0)
        screen.blit(title, (332, 9))
        screen.blit(startbut,(1233,312))
        screen.blit(scorebut,(1346,758))
        draw.rect(screen,(255,0,0),scoreRect,1)
        if mbd and mb[0] and startRect.collidepoint(mx, my):
            start = True

    if start:
        drawScene(screen, offsetx, offsety)  # Draw the background and mask

        playerShield(sprites[0])

        offsetx, offsety = movePlayer(sprites[0], offsetx, offsety)  # Move the player character based on input

        if ku and keys[K_d] == False and keys[K_a] == False and keys[K_w] == False and keys[K_s] == False:
            stop(sprites[0])
        if kd:
            if keys[K_f]:
                charSpeed, charDamage, charDefense, weaponPic = changeMain('Fighter')
            if keys[K_g]:
                if weapons['Shinobi'] in inventory:  # If the player doesn't have a dagger
                    charSpeed, charDamage, charDefense, weaponPic = changeMain('Shinobi')
            if keys[K_h]:
                if weapons['Samurai'] in inventory:  # If the player doesn't have a dagger
                    charSpeed, charDamage, charDefense, weaponPic = changeMain('Samurai')
            if keys[K_SPACE]:
                changeMove(sprites[0], 'Attack_3')
        if mbd:
            if mb[0]:
                changeMove(sprites[0], 'Attack_1')
            if mb[2]:
                changeMove(sprites[0], 'Attack_2')

        for chest in chests:  # Check for chests
            d = hypot(sprites[0][HITBOX].centerx - (chest[0] - offsetx), sprites[0][HITBOX].centery - (chest[1] - offsety))
            if (chest[3] != 1 and d < 50) and not opening:
                currentchest = chest
                print('Q to open chest')
                if keys[K_q] and d < 50:
                    opening = True
            elif (chest[3] == 1 and d < 200) and not opening:
                currentchest = chest
                print('Q to open chest')
                if keys[K_q] and d < 200:
                    opening = True
            if opening :
                currentd = hypot(sprites[0][HITBOX].centerx - (currentchest[0] - offsetx), sprites[0][HITBOX].centery - (currentchest[1] - offsety))
                if currentchest[3] != 1:
                    if currentd > 50 or keys[K_ESCAPE]:
                        opening = False
                else:
                    if currentd > 200 or keys[K_ESCAPE]:
                        opening = False

        # enemy behaviour
        for enemy in sprites[2:]:  # Skip the sprites[0]
            if not respawning:
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
                        if 45 < d < 70:
                            move(enemy, dx / d * 2, dy / d * 2)
                        elif d < 45:
                            stop(enemy)
                            if mill % 2000 < 20:
                                changeMove(enemy, 'Attack_1')
                        elif 70 < d < 150:
                            move(enemy, dx / d * -.75, dy / d * -.75)
                            move(enemy, dx / d * .05, dy / d * .05) # turn to face player
                        else:
                            stop(enemy)
                        if 80 < d < 160 and mill % 7000 < 20:
                            changeMove(enemy, 'Attack_3') # earthquake
                            slowPlayer = True  # Slow the player for a short duration
                            spellStart = mill
                
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

        d, dx, dy = getDist(sprites[1], sprites[0])  # Get distance to boss
        bossHealth = sprites[1][HEALTH]  # Get boss health

        if d > 1000:  # If the player is more than 1000 pixels away from the boss
            if mill % 10000 < 4000:  # Boss attacks every 2 seconds
                move(sprites[1], 1, 0)  # Move towards the player
            else:
                stop(sprites[1])  # Stop if not attacking
            if mill % 10000 > 6000:  # Boss attacks every 2 seconds
                move(sprites[1], -1, 0)  # Move towards the player
            else:
                stop(sprites[1])  # Stop if not attacking
        elif d > 500:
            stop(sprites[1])  # Stop if within 1000 pixels of the boss

        if d < 1000 and fight == 0:  # If the player is within 1000 pixls of the boss
            for sprite in sprites[2:]:  # Skip the player and boss
                kill(sprite)  # Remove all other enemies from the game
            fight = 1  # Set boss fight flag to True
            bossFight = True  # Set boss fight flag to True

        if bossFight:  # If the boss fight is active
            if fight == 1:  # If the boss is alive
                cycle = 10000 # attack cycle length
                if mill % cycle < 2500:
                    move(sprites[1], dx / d * -1, dy / d * -1)  # Move towards the player
                    move(sprites[1], dx / d * 0.1, dy / d * 0.1)  # Move towards the player
                if 2500 < mill % cycle < 4500:
                    if d > 50:  # If the player is more than 100 pixels away
                        move(sprites[1], dx / d * 3, dy / d * 3)  # Move towards the player
                    else:
                        stop(sprites[1])
                        changeMove(sprites[1], 'Attack')
                if 5000 < mill % cycle:
                    stop(sprites[1])  # Stop 
                if 9000 < mill % cycle and d < 50:
                    changeMove(sprites[1], 'Attack')
                if bossHealth < 500:  # If the boss is dead and fight2 is not active
                    fight = 2
                    if len(sprites) < 3:
                        for i in range(4):
                            generateEnemy((4250, 400))  # Generate enemies at predefined spawn points
                        respawnStart = mill
                        respawning = True
            if fight == 2:
                if mill - respawnStart < 7000:
                    move(sprites[1], -4, 0)
                if mill - respawnStart < 5000:
                    for sprite in sprites[2:]:  # Skip the player and boss
                        d, dx, dy = getDist(sprite, sprites[0])  # Get distance to boss
                        if d > 100:
                            move(sprite, dx / d * 1.5, dy / d * 1.5)
                        else:
                            move(sprite, dx / d * -1.5, dy / d * -1.5)
                else:
                    move(sprites[1], .1, 0)
                    respawning = False
                if len(sprites) == 2:
                    fight = 3
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
            if fight == 3:  # If the boss is alive
                cycle = 15000 # attack cycle length
                if mill % cycle < 1000:
                    move(sprites[1], dx / d * -1, dy / d * -1)  # Move towards the player
                    move(sprites[1], dx / d * 0.1, dy / d * 0.1)  # Move towards the player
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
                if 1000 < mill % cycle < 2500:
                    move(sprites[1], chdx / chd * 5, chdy / chd * 5)  # Move towarchds the player
                    if sprites[1][HITBOX].colliderect(sprites[0][HITBOX]):
                        hurt(sprites[0], 10)
                if 2500 < mill % cycle < 3000:
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
                if 3000 < mill % cycle < 4500:
                    move(sprites[1], chdx / chd * 5, chdy / chd * 5)  # Move towarchds the player
                    if sprites[1][HITBOX].colliderect(sprites[0][HITBOX]):
                        hurt(sprites[0], 10)
                if 4500 < mill % cycle < 5000:
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
                if 5000 < mill % cycle < 6500:
                    move(sprites[1], chdx / chd * 5, chdy / chd * 5)  # Move towarchds the player
                    if sprites[1][HITBOX].colliderect(sprites[0][HITBOX]):
                        hurt(sprites[0], 10)
                if 6500 < mill % cycle < 8000:
                    if d > 50:  # If the player is more than 100 pixels away
                        move(sprites[1], dx / d * 3, dy / d * 3)  # Move towards the player
                    else:
                        stop(sprites[1])
                        changeMove(sprites[1], 'Attack')
                if 8000 < mill % cycle:
                    stop(sprites[1])  # Stop 
                if 14200 < mill % cycle and d < 50:
                    changeMove(sprites[1], 'Attack')
                if bossHealth < 250:  # If the boss is dead and fight2 is not active
                    fight = 4
                    for i in range(7):
                        generateEnemy((5500, 400))  # Generate enemies at predefined spawn points
                    respawnStart = mill
                    respawning = True
            if fight == 4:
                if mill - respawnStart < 7000:
                    move(sprites[1], 4, 0)
                if mill - respawnStart < 5000:
                    for sprite in sprites[2:]:  # Skip the player and boss
                        d, dx, dy = getDist(sprite, sprites[0])  # Get distance to boss
                        if d > 100:
                            move(sprite, dx / d * 2, dy / d * 2)
                else:
                    move(sprites[1], .1, 0)
                    respawning = False
                if len(sprites) == 2:
                    fight = 5
            if fight == 5:  # If the boss is alive
                cycle = 15000 # attack cycle length
                if mill % cycle < 1000:
                    move(sprites[1], dx / d * -1, dy / d * -1)  # Move towards the player
                    move(sprites[1], dx / d * 0.1, dy / d * 0.1)  # Move towards the player
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
                if 1000 < mill % cycle < 2500:
                    move(sprites[1], chdx / chd * 5, chdy / chd * 5)  # Move towarchds the player
                    if sprites[1][HITBOX].colliderect(sprites[0][HITBOX]):
                        hurt(sprites[0], 10)
                if 2500 < mill % cycle < 3000:
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
                if 3000 < mill % cycle < 4500:
                    move(sprites[1], chdx / chd * 5, chdy / chd * 5)  # Move towarchds the player
                    if sprites[1][HITBOX].colliderect(sprites[0][HITBOX]):
                        hurt(sprites[0], 10)
                if 4500 < mill % cycle < 5000:
                    chd, chdx, chdy = getDist(sprites[1], sprites[0])  # Get chdistance to player
                if 5000 < mill % cycle < 6500:
                    move(sprites[1], chdx / chd * 5, chdy / chd * 5)  # Move towarchds the player
                    if sprites[1][HITBOX].colliderect(sprites[0][HITBOX]):
                        hurt(sprites[0], 10)
                if 6500 < mill % cycle < 8000:
                    if d > 50:  # If the player is more than 100 pixels away
                        move(sprites[1], dx / d * 3, dy / d * 3)  # Move towards the player
                    else:
                        stop(sprites[1])
                        changeMove(sprites[1], 'Attack')
                if 8000 < mill % cycle:
                    stop(sprites[1])  # Stop 
                if 14200 < mill % cycle and d < 50:
                    changeMove(sprites[1], 'Attack')
                
        updateSprite(sprites[1], 'boss')  # Update the boss sprite

        updateSprite(sprites[0], 'player')

        # if len(sprites) < maxEnemies + 1:  # Limit the number of enemies
        #     generateEnemy(choice(spawnPoints))
        # print(sprites[0][SHIELD])
        drawOverlay(sprites[0][HEALTH])  # Draw the health bar
        drawInventory()

        if showLore and activeLoreItem:
            loreBox = Surface((500, 150))
            loreBox.fill((25, 25, 25))

            for i, line in enumerate(itemLore[activeLoreItem]):
                text = font.SysFont("Georgia", 20).render(line.strip(), True, (255, 255, 255))
                loreBox.blit(text, (10, 10 + i * 30))

            screen.blit(loreBox, (50, 700))
            draw.rect(loreBox, (215, 166, 83), (50,700,500,150), 3)

            # Dismiss X
            draw.rect(screen, (200, 60, 60), (530, 700, 30, 30))
            xFont = font.SysFont("Arial", 24)
            xText = xFont.render("X", True, (255, 255, 255))
            screen.blit(xText, (537, 703))
            xRect = Rect(530, 700, 30, 30)
            if mbd and mb[0] and xRect.collidepoint(mx, my):
                showLore = False

        for item in droppedItems:
                itempic, world_x, world_y = item
                screen.blit(itempic, (world_x, world_y))

        if mbd and mb[0]:  
            for item in droppedItems[:]:
                itempic, x, y = item
                itemRect = Rect(x,y,32,32)
                if itemRect.collidepoint(mx, my) and len(inventory) < 9:
                    inventory.append(itempic)
                    droppedItems.remove(item)
        
        if opening:  # If the chest is being opened
            openChest(currentchest)  # Open the chest if within range and Q is pressed


        if time.get_ticks() % 20000 < 50:
            hunger -= 5
            if hunger < 30:
                slowPlayer = True  # Slow the player if hunger is low
            elif hunger <= 0:
                hurt(sprites[0], 10)
        
        if keys[K_2]:  # If the player presses 2 and hunger is below 200
            eat(0)  # Eat food at position 1
        
        print(gold)
        gameClock.tick(50)
        # print(f'Time: {time.get_ticks()} | FPS: {gameClock.get_fps()}')  # Print FPS for debugging
        # # print(sprites[0][HITBOX].x, sprites[0][HITBOX].y)  # Print player position for debugging
        # # print(offsetx, offsety)  # Print player position for debugging
        # print(sprites[0][HEALTH])  # Print player stats
        # print(getDist(sprites[0], sprites[1]))  # Print distance to boss for debugging
        
    display.flip()
quit()