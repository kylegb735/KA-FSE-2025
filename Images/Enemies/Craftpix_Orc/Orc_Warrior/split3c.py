from pygame import *
import sys, os, glob
os.environ['SDL_VIDEO_WINDOW_POS'] = '80,30'
init()
MOD_KEYS = (K_LCTRL, K_RCTRL, K_LSHIFT, K_RSHIFT, K_LALT, K_RALT)


def picName():
    global screen, back
    screen = display.set_mode((800,600))
    fnt = font.SysFont("Times New Roman", 22)
    names = glob.glob("*.png")
    picked = ""
    while True:
        for e in event.get():
            if e.type == QUIT:
                quit()
                sys.exit(0)
        screen.fill(0)
        for i,n in enumerate(names):
            txt = fnt.render(n,True,(255,255,0))
            screen.blit(txt,(50,50+i*30))

        mx,my = mouse.get_pos()
        mb = mouse.get_pressed()
        if not mb[0] and picked != "":
            return picked
        for i in range(len(names)):
            if mx > 50 and mx < 350:
                y = 50 + i*30
                if my > y and my < y+30:
                    draw.rect(screen,(255,0,0),(50,y,300,29),1)
                    if mb[0]:
                        picked = names[i]
        display.flip()                 


def setImage():
    global pic, back, screen, wid, hi,bgCol,offx,offy
    offx,offy = 0,0
    fname = picName()

    pic = image.load(fname)   

    wid,hi = 1000,600
    # wid,hi = pic.get_size()
    back = Surface((wid+2,hi+2),SRCALPHA)
    back.fill((pic.get_at((0,0))))
    back.blit(pic,(1,1))
    bgCol = back.get_at((0,0))
    screen = display.set_mode((wid+2,hi+2))
    screen.blit(pic,(1,1))
    display.flip()

setImage()

''' -------------------------------------------------------------
    getName
    -------------------------------------------------------------
    Because pygame likes to crash you can copy and paste my getName
    function into your program and use it, free of charge.  You
    may want to change the size of the rectange, it's location, the
    font, and the colour so that it matches your program.
    ------------------------------------------------------------- '''
def getName():
    ans = ""                    # final answer will be built one letter at a time.
    arialFont = font.SysFont("Times New Roman", 16)
    back = screen.copy()        # copy screen so we can replace it when done
    textArea = Rect(5,5,200,25) # make changes here.
    
    typing = True
    while typing:
        for e in event.get():
            if e.type == QUIT:
                event.post(e)   # puts QUIT back in event list so main quits
                return ""
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    typing = False
                    ans = ""
                elif e.key == K_BACKSPACE:    # remove last letter
                    if len(ans)>0:
                        ans = ans[:-1]
                elif e.key == K_KP_ENTER or e.key == K_RETURN : 
                    typing = False
                elif e.key < 256:
                    ans += e.unicode       # add character to ans
                    
        txtPic = arialFont.render(ans, True, (0,0,0))   #
        draw.rect(screen,(220,255,220),textArea)        # draw the text window and the text.
        draw.rect(screen,(0,0,0),textArea,2)            #
        screen.blit(txtPic,(textArea.x+3,textArea.y+2))        
        display.flip()
        
    screen.blit(back,(0,0))
    return ans

def lineHasPixel(y,area):
    for x in range(area[0],area[2]+1):
        if back.get_at((x,y))!=bgCol:
            return True
    return False

def findPixelLine(y,area):
    while y<area[3] and not lineHasPixel(y,area):
        y+=1
    return y

def findOpenLine(y,area):
    while y<area[3] and lineHasPixel(y,area):
        y+=1
    return y

def colHasPixel(top,bott,x):
    for y in range(top,bott+1):
        if back.get_at((x,y))!=bgCol:
            return True
    return False

def findPixelCol(top,bott,x):
    while x<wid and not colHasPixel(top,bott,x):
        x+=1
    return x

def findOpenCol(top,bott,x):
    while x<wid and colHasPixel(top,bott,x):
        x+=1
    return x

def getMods():
    mods = key.get_mods()
    return KMOD_SHIFT & mods > 0, KMOD_CTRL & mods > 0, KMOD_ALT & mods > 0

def showAnchor(x,y):
    draw.circle(screen,(255,255,255),(x, y),5)
    draw.circle(screen,(0,0,0),(x, y),4)
    draw.circle(screen,(255,0,0),(x, y),3)    

def getCurrent(pos, rects):
    current = -1
    for i, r in enumerate(rects):
        if r.collidepoint(pos):
            current = i
    return current

def moveAnchors(rects, mpos, anchors):
    shift, ctrl, alt = getMods()
    for i,r in enumerate(rects):
        if r.collidepoint(mpos):
            left = mpos[0] - r.left
            down = mpos[1] - r.h*2
            if i>0:
                if shift:
                    down = anchors[i-1][1]
                if ctrl:
                    left = anchors[i-1][0]
            anchors[i] = (left, down)
            
def mergeImages(pics):
    width = sum([p.get_width() for p in pics])
    pic = Surface((width, pics[0].get_height()),SRCALPHA)
    # pic.fill((back.get_at((0,0)))) # I may need this
    x = 0
    for p in pics:
        pic.blit(p, (x, 0))
        x += p.get_width()
    return pic

def makeRects(pics):
    #print("CALL MAKE RECTS")
    totalWidth = 0
    height = max([p.get_height() for p in pics])
    rects = []
    anchors = []
    for p in pics:
        r1 = p.get_rect()
        r = Rect(totalWidth, height*2, r1.w, height)
        r.w += 5
        rects.append(r)
        totalWidth += r.w
        anchors.append((r.width//2, r.height//2))
        
    return rects, anchors, totalWidth

def showMove(pics):
    ''' pics - List of surfaces that make one move
    - The purpose of this function is to all you to preview the move, stabalize it,
    and save the frames. You stabalize by moving the red circle to a consistant place on each
    frame.
    - hold shift - it will use the y value of the anchor to the left
    - hold ctrl - it will use the x value of the anchor to the left
    
'''
    global screen
    display.set_caption("Shift - keep same y as previous Ctrl - keep same x as previous Alt + left - merge Alt + right - split")
    running = True
    #cop = screen.copy()
    rects, anchors, totalWidth = makeRects(pics)
    #print(rects, anchors)
    height = rects[0].h
    w,h = screen.get_size()
    # expand window if all the moves don't fit
    if totalWidth > w:
        screen = display.set_mode((totalWidth,h))
    frame = 0
    current = -1 # the one you clicked on for merging frames
    backCol = (255,222,222) if bgCol.a == 0 else bgCol
    screen.fill(backCol)
       
    while running:
        for evnt in event.get():               
            if evnt.type == QUIT:
                running = False
            if evnt.type == MOUSEBUTTONDOWN:
                if alt:
                    # merge
                    if evnt.button == 1:
                        current = getCurrent(evnt.pos, rects)
                    if evnt.button == 3:
                        curr = getCurrent(evnt.pos, rects)
                        r = rects[curr]
                        p = pics[curr]
                        p1 = p.subsurface(0,0,mx-r.x,r.h).copy()
                        p2 = p.subsurface(p1.get_width(), 0, r.w - p1.get_width()-5, r.h).copy()
                        pics[curr] = p1
                        pics.insert(curr+1, p2)
                        rects, anchors, totalWidth = makeRects(pics)
                        
        
            if evnt.type == MOUSEBUTTONUP:
                if evnt.button == 1:
                    if current>=0:
                        dest = getCurrent(evnt.pos, rects)
                        pics[current] = mergeImages(pics[current: dest+1])
                        del pics[current+1: dest+1]
                        rects, anchors, totalWidth = makeRects(pics)
                    current = -1

            if evnt.type == KEYDOWN:
                if evnt.key not in MOD_KEYS:
                    running = False

        mx, my = mpos = mouse.get_pos()
        mb = mouse.get_pressed()
        shift, ctrl, alt = getMods()
        
        if mb[0]==1:
            moveAnchors(rects, mpos, anchors)
                    
        frame+=1
        draw.rect(screen,backCol,(0,0,screen.get_width(),height*3))

        maxax = max([a[0] for a in anchors])
        maxay = max([a[1] for a in anchors])

        f = frame//10 % len(pics)
        screen.blit(pics[f],((maxax-anchors[f][0])%screen.get_width(),maxay-anchors[f][1]))

        for i,pic in enumerate(pics):
            screen.blit(pics[i],rects[i])
            draw.rect(screen, 0, rects[i], 1)
            
        for i,a in enumerate(anchors):
            showAnchor(rects[i].x + a[0], rects[i].y + a[1])
            if alt and not mb[0]:
                if rects[i].collidepoint(mpos):
                    draw.line(screen, (0,0,255),(mx, rects[i].top),(mx,rects[i].bottom),3)
            
        if current >= 0:
            draw.line(screen, (255,255,0), rects[current].center, mpos,5)
        
        time.wait(20)
        display.flip()
    display.set_caption("Draw box around move and press space")

    return anchors, pics
    #screen.blit(cop,(0,0))

# 
def getMoveV(area):
    pics = []

    # get rid of extra padding from left and right of the area
    left = findPixelCol(area[1], area[3], area[0])
    right = findOpenCol(area[1], area[3], left)
    bott = area[1]
    while bott<area[3]:
        top = findPixelLine(bott, area)
        if top >= area[3]:break
        bott = findOpenLine(top, area)        
        if bott-top>5:
            pics.append(back.subsurface((left,top,right-left+1,bott-top+1)))
    return pics

            
def getMove(area):
    pics = []
    if area[3]-area[1] > area[2]-area[0]:
        pics = getMoveV(area)
    else:
        top = findPixelLine(area[1],area)
        bott = findOpenLine(top,area)
        right = area[0]
        while right<area[2]:
            left = findPixelCol(top,bott,right)
            if left >= area[2]:break
            right = findOpenCol(top,bott,left)
            if right-left>5:
                pics.append(back.subsurface((left,top,right-left+1,bott-top+1)))

    if len(pics)==0:return
    anchors, pics = showMove(pics)
    maxax = max([a[0] for a in anchors])
    maxay = max([a[1] for a in anchors])

    name = getName()
    if name == "":
        return
    else:
        if name not in os.listdir("."):
            os.mkdir(name)
        for i,pic in enumerate(pics):
            extrax = maxax-anchors[i][0]
            extray = maxay-anchors[i][1]
            tmp = Surface((pic.get_width()+extrax,pic.get_height()+extray),SRCALPHA)
            tmp.fill((0,0,0,0))
            pic = pic.convert()
            pic.set_colorkey((bgCol))
            tmp.blit(pic,(extrax,extray))
            image.save(tmp,name+"/"+name+str(i)+".png")
            
running = True
display.set_caption("Draw box around move and press space")

cop = screen.copy()
stx,sty = 0,0
offx,offy = 0,0
singlex,singley =0,0

while running:
    for evnt in event.get():               
        if evnt.type == QUIT:
            running = False
        if evnt.type == MOUSEBUTTONDOWN and evnt.button==4 and offy>0:
            offy -= 10
        if evnt.type == MOUSEBUTTONDOWN and evnt.button==5:
            offy += 10
        if evnt.type == MOUSEBUTTONDOWN and evnt.button in [1,3]:
            stx,sty = evnt.pos
            
        if evnt.type == MOUSEBUTTONUP:
            ex,ey = evnt.pos
            ex = max(1,ex)
            ex = min(back.get_width()-2,ex)
            ey = max(1,ey)
            ey = min(back.get_height()-2,ey)
            if evnt.button==1:
                getMove([min(stx,ex),min(sty+offy,ey+offy),max(ex,stx),max(sty+offy,ey+offy)])
            #if evnt.button == 3:  # I want to add the ability to get just one image
            #    getImage([min(stx,ex),min(sty+offy,ey+offy),max(ex,stx),max(sty+offy,ey+offy)])
            #screen.blit(cop,(0,0))
            
    mx,my = mouse.get_pos()

    keys = key.get_pressed()
    if keys[K_DOWN]:
        offy += 10
    if keys[K_UP] and offy>0:
        offy -= 10
    if keys[27]:
        setImage()
    screen.fill((255,0,255))
    screen.blit(back,(0,-offy))
        
    if mouse.get_pressed()[0]==1:
        draw.rect(screen, (0,255,0), (stx,sty, mx-stx+1,my-sty+1),1)
      
    display.flip()
    
     
quit()
