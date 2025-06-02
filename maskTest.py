
from pygame import *
screen = display.set_mode((1600,900))

def drawScene(screen,x,y):
    ''' As always, ALL drawing happens here '''
    screen.blit(mapp,(-x,-y))
    draw.circle(screen, (255,0,0), (800,450),5)         
    display.flip()


def clear(mx,my):
    ''' This returns whether a pixel is clear or not. The function get_at crashes
        if you try to get a pixel that is not on the picture. Because of this I like to
        call it from another function. If x,y is not on the mask then I return False. This
        will happen when our hero tries to go off the map.

        If the pixel is on the map we return True if the corresponding pixel on the mask is
        not blue. '''
    if mx<0 or mx >= mask.get_width() or my<0 or my >= mask.get_height():
        return False
    else:
        return mask.get_at((mx,my)) != WALL

def move(x,y):
    ''' check, on the mask, 7 pixels away in the direction they are trying to move.
      7, because the guy has radius 5 and they are moving 2.'''
    if keys[K_UP] and clear(800 + x,450 + y - 7):
        y -= 2
    if keys[K_DOWN] and clear(800 + x,450 + 7 + y):
        y += 2
    if keys[K_LEFT] and clear(800 + x - 7,450 + y):
        x -= 2
    if keys[K_RIGHT] and clear(800 + x + 7, 450 +y):
        x += 2

    return x,y
      
myClock = time.Clock()
mask = image.load("Images/Maps/mask.png")
mapp = image.load("Images/Maps/map.png")
WALL = (225,135,250,255)

x = 10
y = 55

running = True
while running:
    for evnt in event.get():
        if evnt.type == QUIT:
            running = False

    keys = key.get_pressed()
    if keys[K_ESCAPE]: break
    screen.fill(0)
    x,y = move(x,y)

    drawScene(screen,x,y)
                    
    display.flip()
    myClock.tick(60)                        
    
quit()