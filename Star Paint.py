## James Xu
## ICS3U
## Paint Program
## Theme: Star Trek
##Extra Features
##- Undo and Redo
##- Fill
##- Smooth Rectangle
##- Smooth Ellipse
##- Save Color
##- If mouse is over a button, it turns blue
##- Selected button turns red
##- Change thickness and size using scroll wheel
##- Crop tool
##- Rotate
##- Polygon Tool
##Attention to Detail
##- OS specific modifier keys are used
##- Drawing space is just the right size, with a little gap for smoothness
##- Button colors follow the LCARS palette
##- Smooth transform is used to reduce pixelation
##- Color wheel collidepoint only changes color if the mouse is ON the wheel, not just in its rectangle
from pygame import *
import pickle
import os, sys
from itertools import chain
import random
from tkinter import *
from tkinter import filedialog
import math
import threading
font.init()
tcm = font.Font('tcm.ttf',24)#Font for size display
root = Tk()
root.attributes("-topmost", True)#When Tk is activated for file dialog, make it top most
icon = image.load('non-load_assets/icon.png')#Program Icon
display.set_icon(icon)#Set window icon
display.set_caption('Star Paint')#Set Window Caption
operating_system = sys.platform#Get operating system
shift_key = K_LSHIFT
if operating_system == 'darwin':#If OS == Darwin (macOS) use 'Command' instead of control
    control_modifier = 310
else:
    control_modifier = K_LCTRL#Otherwise use Left Control
imageAssets = [names for names in os.listdir('menu1') if names.endswith('.png')]#Find the names of all the images for Menu 1
imageAssetsMenu2 = [names for names in os.listdir('menu2') if names.endswith('.png')]#Find the names of all the images for Menu 2
image_load = {file[:file.find('.')]: image.load('menu1/'+file) for file in imageAssets}#Load the images of all the images for Menu 1
image_loadMenu2 = {file[:file.find('.')]: image.load('menu2/'+file) for file in imageAssetsMenu2}#Load the images of all the images for Menu 2
image_as_object = {}#Dictionary for images to be stored in this format- mode: image object
screen = display.set_mode((1440, 900))
imageAssetsMenu3 = [names for names in os.listdir() if names.endswith('.png') and names != 'Paint2.png']
running = True
##gif_assets = [transform.scale(image.load('GIF/'+i).convert(),(200,150)) for i in os.listdir('GIF')]
gif_counter = 0
mode = 'pencil'#Default mode is pencil
color = (55, 153, 251)#Default color
screen.fill((0, 0, 0))
drawSpace = Rect(258, 102, 1042, 561)#Canvas rectangle for clipping and collidepoint
background = image.load('Paint2.png')#Background
screen.blit(background, (0, 0))
y = [195+i*60 for i in range(len(imageAssetsMenu3))]
for i in imageAssetsMenu3:
    image_as_object[i[:i.find('.')].lower()+'Tool'] = screen.blit(transform.smoothscale(image.load(i),(110,38)),(1315,y[imageAssetsMenu3.index(i)]))
dragging = False#dragging Flag to see if mouse is being dragged
drew = False#flag for if user drew something
redo = []#List to store 'undoed' screen copies
root.withdraw()
###
copy_list = []#List of screen.copy()s for use in undoing
###
omx,omy = (0,0)#initialize omx,omy as (0,0) to avoid errors of variable not existing
def drawRect(x,y,nx,ny,s,c):#Custom draw rectangle function to make it smoother and fill in missing corners
    r = Rect(x,y,nx-x,ny-y)
    r.normalize()
    x,y,nx,ny = r
    nx = nx+x
    ny = ny+y
    if 2*s < min(abs(nx-x),abs(ny-y)):
        x += s//2  # Adjust x,y values to
        y += s//2  # get rid of jumpiness when moving from drawing an unfilled rect to filled
        nx -= s//2 # Adjust nx,ny for same reason as above
        ny -= s//2 #
        draw.rect(screen, (c), (x,y,nx-x,ny-y),s)
        if s != 0:
            y -= 1
            x -= 1
            nx -= 1
            ny -= 1 ## below code is to draw in the main rectangle and the missing corners
            draw.rect(screen, (c), (x,y,nx-x,ny-y),s)
            draw.rect(screen, (c), (x-(s/2)+1,y-(s/2)+1,(s/2)+1,(s/2)+1))
            draw.rect(screen, (c), (nx,y-(s/2)+1,(s/2)+1,(s/2)+1))
            draw.rect(screen, (c), (x-(s/2)+1,ny,(s/2)+1,(s/2)+1))
            draw.rect(screen, (c), (nx,ny,(s/2)+1,(s/2)+1))
    else:
        draw.rect(screen,(c),(x,y,nx-x,ny-y),0) #If width is not big enough for thickness, just draw an unfilled rect
    return Rect(x,y,nx-x,ny-y)
def drawLine(x,y,nx,ny,s,c):#Completely useless function, same function as draw.line(), but easier to remember function arguments
    draw.line(screen, (c),(x,y),(nx,ny),s)
    return None
def drawEllipse(x,y,nx,ny,s,co):#Custom ellipse drawing function to make it smooth
    e_rect = Rect(x,y,nx-x,ny-y)
    e_rect.normalize()
    if 2*s < min(abs(nx-x),abs(ny-y)): #Check if radius is less than width
        pass
    else:
        s = 0#If not, just draw filled ellipse
    if s > 0:#Below is code to make ellipse smooth
        a,b,c,d = e_rect
        alpha = Surface((c,d))#new surface is made the same size as the ellipse rectangle
        alpha.set_colorkey((1,1,1))# (1,1,1) is a color that is not in the palette, making it safe to use as color key
        alpha.fill((1,1,1))#Fill the rectangle with transparent color
        draw.ellipse(alpha, (co), (0,0,c,d))#Draw a filled ellipse in the user selected color
        draw.ellipse(alpha, (1,1,1),(s,s,c-s-s,d-s-s),0)#Draw a second smaller transparent ellipse that is inside the main one to achieve thickness effect
        screen.blit(alpha, (a,b))
    else:
        draw.ellipse(screen, (co), e_rect,0)#If size is 0 (filled) just draw a filled)

    return None
y = list(chain.from_iterable((i, i) for i in range(195, 375, 60)))#List of y coords. Chained because two icons at each y pos
count = 0
for Dkey, i in image_load.items():#Put blitted image in a dictionary
    image_as_object[Dkey] = screen.blit(transform.smoothscale(i, (110, 38)), ([5, 140][count % 2], y[count]))
    count += 1
count = 0
for Dkey,i in image_loadMenu2.items():
    image_as_object[Dkey] = screen.blit(transform.smoothscale(i, (110, 38)), ([5, 140][count % 2], 396))
    count += 1
##Stamp Tool
ratio = 1#Ratio for resizing
y = list(chain.from_iterable((i, i) for i in range(470, 749, 93)))#Y coordinates for stamps. Chained because 2 images at each y pos
stampAssets = []
for names in os.listdir('stamps'):#Find then load stamps
    if names.endswith('.jpg') or names.endswith('.png') or names.endswith('.jpeg'):
        stampAssets.append(image.load('stamps/'+names))
count = 0#Reset count for further use in code
menuIcons = []#List of menu icon stamp images that have been scaled
for i in range(len(stampAssets)):
    menuIcons.append(screen.blit(transform.smoothscale(stampAssets[i], (50,50)), ([33,172][i % 2], y[i])))
selected = {str(key): (221,255,255) for key in menuIcons}#Color value for selection feedback for each menu icon
current_stamp = 0#Current Stamp value. 0 means that mode is not Stamp
##Color Selection
c_wheel = screen.blit(image.load('non-load_assets/cwheel.png'),(298,720))#Color wheel
saved_colors = [(255,255,255) for i in range(6)]#Color of each of the color selection boxes
c_box_x = [700+(x*100) for x in range(6)]#x coords for color boxes
c_boxes = []#List of drawn color rectangles
for x in c_box_x:
    draw.rect(screen, (221,255,255), (x,770,50,50), 2)
    c_boxes.append(draw.rect(screen, (255,255,255), (x+2,772,47,47), 0))
c_coords = [Rect(x+2,772,47,47) for i in c_box_x]
draw.rect(screen, (255,255,255),(499,759,72,72),1)
##Polygon Tool
poly_points = []#List of points for polygon
finished_poly = False#Flag to check if polygon is done drawing

##Rotate Tool
rdone = False#Flag to see if rectangle is done drawing. Also used for move tool and crop tool
##Move Tool
first_time = False#See if a new selection rectangle is needed to be drawn. Takes a copy of the screen to avoid selecting the red selection rectangle
##Text Tool
request_exit = False#Flag from event loop that signifies that typing is done
cursor_counter = 0#Only activates the cursor every so often to achieve blinking effect
msg = ''
typing = False
display.flip()
base = screen.copy()
size = 5#Starting size for non shape tools
shape_size = 5#Starting size for shape tools
while running:
    only_undo_once = False
    if len(copy_list) > 100:
        copy_list = copy_list[-99:]#Limit length of copy list to avoid memory errors
    status = {'mbdown':0,'mbup':0,'motion':0}#Dictionary of major event loop statuses that are commonly used
    for e in event.get():
        if e.type == QUIT:
            running = False#When running is false, program quits
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            status['mbdown'] = 1
        if e.type == MOUSEBUTTONUP and e.button == 1:
            status['mbup'] = 1
            if drawSpace.collidepoint(mx,my):
                if mode != 'textTool' and mode != 'cropTool' and mode != 'polyTool' and mode != 'rotateTool' and mode != 'moveTool':#These modes require different approaches to making a screen.copy()
                    copy = screen.copy()
                    copy_list.append(copy)
                    redo = []#If user has drawn, empty redo list
                drew = False#Flag to see if user has drawn anything for pencil and eraser tool
                done_drawing = True
        if e.type == MOUSEBUTTONDOWN and e.button == 4:
            if size > 6:#Minimum size for tools
                size -= 1
            if ratio > 0.2:
                ratio -= 0.1
            if shape_size > 0:
                shape_size -= 1
        if e.type == MOUSEBUTTONDOWN and e.button == 5:
            size += 1
            shape_size += 1
            if ratio < 3:#Maximum size for stamps
                ratio += 0.1
        if e.type == MOUSEMOTION:
            status['motion'] = 1
        if e.type == KEYDOWN:
            only_undo_once = True#Flag that makes user only undos when the key is pressed, not held
            if typing:#Get text for text tool
                if e.key == K_BACKSPACE:
                    if len(msg) > 0:
                        msg = msg[:-1]#Delete a character when backspace is pressed
                elif e.key == K_KP_ENTER or e.key == K_RETURN:
                    request_exit = True#Stop typing when return is pressed
                elif e.key < 256:
                    msg += e.unicode#Add letter to text
                
##    copied = screen.copy()
    mx, my = mouse.get_pos()#get mouse position
    m = mouse.get_pressed()#get if mouse is pressed
    valid = False#Check if pixelarray is disabled
    done_drawing = False
    try:
        pxarray = 0
        valid = True#Disables pixelarray
    except:
        pass
    if valid and mode != 'pencil' and mode != 'eraser':
        try:
            screen.blit(copy_list[-1],(0,0))#Blits a copy of the screen if mode not pencil or eraser
        except:
            screen.blit(base,(0,0))#If list is empty, blit empty screen
    elif valid and (mode == 'pencil' or mode == 'eraser'):
        if done_drawing:
            try:
                screen.blit(copy_list[-1],(0,0))#Only blit if pencil or eraser is done drawing
            except:
                screen.blit(base,(0,0))
    screen.set_clip(None)#Reset Clip to be None for drawing outside canvas
    if shape_size == 0:
        stxt = tcm.render('0 (Filled), Ratio: ' + str(int(ratio*100))+'%', True, (0,0,0))#If shape size is 0 (unfilled) tell user that
    else:
        stxt = tcm.render(str(shape_size) + ', Ratio: ' + str(int(ratio*100))+'%', True, (0,0,0))#Else, just display size
    tss = base.copy().subsurface(Rect(0,740,260,140))#Area underneath shape text
    screen.blit(tss, (0,740))#Blit subsurface of no text under to avoid ugly remains when reblitting text over text
    screen.blit(stxt, (80,781))#Blit text
##    if gif_counter % 10 == 0:#Every 10th cycle of loop, blit one frame
##        a,b,c,d = [25,15,200,150]#Position of gif in Rect() format
##        subsurface_gif = base.copy().subsurface(Rect(a,b,c,d))
##        screen.blit(subsurface_gif,(a,b))#Blit subsurface to avoid problem of gif overlapping old gif
##        screen.blit(gif_assets[gif_counter//10],(25,15))#Blit the gif
    gif_counter += 1
##    if gif_counter >= 10*len(gif_assets):#Reset once counter exceeds 10 * length of list to avoid index error
##        gif_counter = 0
    for i in image_as_object.keys():#Loop through blitted tool icons
        buttonRect = image_as_object[i]
        a,b,c,d = buttonRect
        c+=1
        d+=1
        a-=1
        b-=1
        draw.rect(screen,(221,255,255),(a,b,c,d),1)#Draw a white rectangle around the icon
        if buttonRect.collidepoint(mx,my):
            draw.rect(screen,(153,204,255),(a,b,c,d),1)#If hover, draw a blue rectangle
        if i == mode:
            draw.rect(screen,(245,23,60),(a,b,c,d),1)#If it's the selected mode, draw red rectangle
    for i in menuIcons:
        if mode != 'stamps':
            selected = {str(key): (221,255,255) for key in menuIcons}#Dictionary containing colors of the outlines of menuIcons
        a,b,c,d = i#Rect() values for every rectangle
        c += 1#Adjusted start pos and size to fit around menu icons
        d += 1
        a -= 1
        b -= 1
        draw.rect(screen,selected[str(i)],(a,b,c,d),1)#Draw the rectangle at the color indicated in dictionary
        if i.collidepoint(mx,my):
            draw.rect(screen,(153,204,255),(a,b,c,d),1)#If hover, draw in light blue

    if m[0] == 1 and((mx-(298+75))**2+(my-(720+75))**2)**0.5 <= 75:
        color = screen.get_at((mx,my))#Only change color if mouse distance is within radius
    for b in range(len(c_boxes)):#For loop to go through all the color boxes
        if c_boxes[b].collidepoint(mx,my) and m[0] == 1:
            color = screen.get_at((mx,my))[:-1]#If left click, change color to square color
        elif c_boxes[b].collidepoint(mx,my) and m[2] == 1:#If right click, change color of square to be current color
            saved_colors[b] = color
            draw.rect(screen, (color), c_boxes[b], 0)
            display.update(c_coords[b])
    draw.rect(screen, (color),(500,760,70,70),0)#Draw a square of the current color to display to user
    screen.set_clip(drawSpace)#Reset the clip to be the canvas
    if drawSpace.collidepoint(mx,my) != True:
        for name, img in image_as_object.items():#If mouse is not on canvas, loop through the blitted tools
            if img.collidepoint(mx, my) and status['mbdown'] == 1:
                mode = name
                if name == 'moveTool':
                    first_time = True#First time variable changes to indicate that rectangle selection is needed
                if name == 'polyTool':
                    poly_points = []#Fresh list for drawing polygons
                if name == 'pencil':
                    startPos = [0,0]#Reset variables
                    endPos = [0,0]
        for rec in menuIcons:
            if rec.collidepoint(mx,my) and status['mbdown'] == 1:#If mouse clicks any stamps, set mode to be stamps
                mode = 'stamps'
    if mode == 'openbutton':
        fname = filedialog.askopenfilename(defaultextension='*.png',
                                      filetypes=[('PNG','*.png'),('JPG','*.jpeg'),('Other','*.*')])#Get file name with Tkinter
        if len(str(fname)) != 0:#If file name isn't empty (user didn't cancel) then load the image on to the canvas
            with open(fname, 'rb') as load_file:
                screen.blit(transform.smoothscale(image.load(load_file),(1042,561)),(258,102))
                copy_list.append(screen.copy())
        mode = None
    elif mode == 'savebutton':
        saveContents = screen.subsurface(drawSpace)#Subsurface the canvas
        result = filedialog.asksaveasfilename(defaultextension='*.png',
                                              filetypes=[('PNG','*.png')])#Ger file name
        if len(str(result)) != 0:#If result isn't blank, proceed to save the image
            with open(result, 'wb') as file:
                image.save(saveContents, result)
        mode = None
    elif mode == 'pencil':
        ready_to_copy = False
        if m[0] == 1:#If user clicks, get delta x, delta y, and largest value of those two
            dx = omx-mx
            dy = omy-my
            dist = max(abs(dx),abs(dy))
            if dist == 0:
                dist = 1
            drew = True#Flag to see if user has drawn
        if status['motion'] == 1:
            if drew:#If the mouse moves and the user drew, loop through each pixel point and draw a circle
                for i in range(int(dist)):
                    x = int(mx+i/dist*dx)
                    y = int(my+i/dist*dy)
                    draw.circle(screen,color,(x,y),size//2)
                ready_to_copy = True#Once user circle interpolation has finished, program is ready to take a copy of the screen
            omx,omy = mouse.get_pos()#New mouse position
    if m[0] == 0 and drew:
        drew = False#Once user lets go of mouse, drew variable resets
    elif mode == 'eraser':#Same as above, except color is black
        ready_to_copy = False
        if m[0] == 1:
            dx = omx-mx
            dy = omy-my
            dist = max(abs(dx),abs(dy))
            if dist == 0:
                dist = 1
            drew = True
        if status['motion'] == 1:
            if drew:
                for i in range(int(dist)):
                    x = int(mx+i/dist*dx)
                    y = int(my+i/dist*dy)
                    draw.circle(screen,0,(x,y),size//2)
                ready_to_copy = True
            omx,omy = mouse.get_pos()
    elif mode == 'rectTool':
        if status['mbdown'] == 1:
            startPos = [mx,my]#When user clicks, remember that as the starting position
            dragging=True#Variable that changes to True during the dragging phase of drawing a rectangle
        if dragging:
            endPos = [mx,my]#When dragging, endPos is the new position of the mouse
            drawRect(startPos[0],startPos[1],endPos[0],endPos[1],shape_size,color)#Draw a rectangle from startPos to endPos
        if status['mbup'] == 1 and dragging:
            dragging=False#When user lets go, drawing finishes and dragging resets
    elif mode == 'lineTool':#Same as above, except draws line
        if status['mbdown'] == 1:
            startPos = [mx,my]
            dragging=True
        if dragging:
            endPos = [mx,my]
            drawLine(startPos[0],startPos[1],endPos[0],endPos[1],size,color)
        if status['mbup'] == 1 and dragging:
            dragging=False
    elif mode == 'ellipseTool':#Same as above two, except draws ellipse
        if status['mbdown'] == 1:
            startPos = [mx,my]
            dragging=True
        if dragging:
            endPos = [mx,my]
            drawEllipse(startPos[0],startPos[1],endPos[0],endPos[1],shape_size,color)
        if status['mbup'] == 1 and dragging:
            dragging=False
    elif mode == 'fillTool':
        if m[0] == 1 and drawSpace.collidepoint(mx,my):
            perm_points = set()#Keep track of the points that have been filled
            rcn = screen.map_rgb(color)#Replacement color in pygame format
            pxarray = PixelArray(screen)#Initialize pixelarray
            dcn = pxarray[mx,my]#color that was at the starting pixel location
            fillPoints = set([(mx,my)])#Queued pixel locations to check using BFS
            while fillPoints:
                px,py = fillPoints.pop()#Pop from queue to check if that pixel location is valid for filling
                oldColor = pxarray[px,py]#color before filling at pixel point
                if oldColor == dcn and 258<px<258+1042-1 and 102<py<102+561-1 and (px,py) not in perm_points:
                    perm_points.add((px,py))
                    pxarray[px,py] = rcn
                    fillPoints.add((px+1,py))#add these pixels below to queue for checkign
                    fillPoints.add((px,py+1))
                    fillPoints.add((px-1,py))
                    fillPoints.add((px,py-1))
    elif mode == 'stamps':
        if current_stamp != 0:
            last_stamp = menuIcons[stampAssets.index(current_stamp)]#If currennt stamp isn't 0, last chosen stamp is set
        else: last_stamp = 0#Placeholder value so code doesn't error
        for i in menuIcons:
            if i.collidepoint(mx,my) and status['mbdown'] == 1:#Loop through menu icons of stamps and check if user is trying to change stamps
                current_stamp = stampAssets[menuIcons.index(i)]
                selected[str(i)] = (245,23,60)#Change the color of the menu icon outline for current stamp
                if last_stamp != i:
                    selected[str(last_stamp)] = (221,255,255)#Change color back if it's not current stamp anymore
        if current_stamp != 0:
            ox,oy = current_stamp.get_size()#size of stamps for resize
            stamp = transform.smoothscale(current_stamp, (int(ox*ratio),int(oy*ratio)))#resize stamp to resizing ratio
            ix,iy = stamp.get_size()#New size of stamp
        if m[0] == 1 and drawSpace.collidepoint(mx,my):
            screen.blit(stamp,(mx-(ix/2),my-(iy/2)))#Blit the stamp where the center of the stamp is the mx,my value
    elif mode == 'cropTool':
        if drawSpace.collidepoint(mx,my):
            if status['mbdown'] == 1:#BEGIN
                startPos = [mx,my]
                dragging=True
            if dragging:            #This section does the same thing as it does above in rectTool, ellipseTool, lineTool
                endPos = [mx,my]#END
                last = drawRect(startPos[0],startPos[1],endPos[0],endPos[1],2,(255,0,0))#rectangle after dragging is finished
            if status['mbup'] == 1 and dragging:
                dragging=False
                a,b,c,d = last#User selected rectangle
                tempCopy = screen.copy()
                cropSurface = transform.smoothscale(tempCopy.subsurface(Rect(a+4,b+4,c-5,d-5)),(1042,561))#[1]
                #[1] -- Subsurfaces selected rectangle and makes it the size of the canvas
                baseCopy = base.copy()
                screen.blit(cropSurface,(258,102))#Blit subsurfaced area on to screen
                copy_list.append(screen.copy())
                redo = []#Empty redo list
    elif mode == 'polyTool':
        ##BEGIN @[2]
        if len(poly_points) > 2 and ((mx-poly_points[0][0])**2+(my-poly_points[0][1])**2)**0.5 < 10 and finished_poly == False:
            draw.line(screen,color,poly_points[-1],poly_points[0],5)
            if status['mbdown'] == 1:
                poly_points.append(poly_points[0])
                finished_poly = True
        ##END @[2]
        ##@[2] -- Check if a polyfon is possible and then if mouse is within 10 pixel distance.
        ##        If user clicks, then complete rectangle
        elif status['mbdown'] == 1 and drawSpace.collidepoint(mx,my) and finished_poly == False:
            draw.circle(screen, color, (mx,my), 10, 0)#Draw circle at mouse position to show that is mouse position
            dragging = True
        if dragging:
            draw.circle(screen, color, (mx,my), 10, 0)
            if len(poly_points) > 0:
                endPos = (mx,my)#When dragging, draw a line between previous point and mouse position
                draw.line(screen,color,poly_points[-1],endPos,5)
        if status['mbup'] == 1 and drawSpace.collidepoint(mx,my) and not finished_poly and dragging:
            poly_points.append((mx,my))#When user lets go, append mouse position to list
            dragging = False
        for i in range(1,len(poly_points)):
            draw.line(screen,color,poly_points[i-1],poly_points[i],5)#Loop through everytime and connect the dots
        if len(poly_points) > 0 and not finished_poly:
            draw.circle(screen, (0,255,0), poly_points[0],10,0)#Draw a green circle at beginning pos
            draw.circle(screen, (255,0,0), poly_points[-1],10,0)#Draw a red circle at last position
        if finished_poly:
            if shape_size == 0:#If user wants filled shapes, draw filled shapes
                draw.polygon(screen,color,poly_points)
            copy_list.append(screen.copy())
            poly_points = []#If polygon is finished, empty list and copy screen
            finished_poly = False
            redo = []#Empty redo list
    elif mode == 'rotateTool':
        if drawSpace.collidepoint(mx,my):
            if not rdone:
                ## SECTION BEGIN
                if status['mbdown'] == 1 and not rdone:
                    startPos = [mx,my]
                    dragging=True
                if dragging:
                    endPos = [mx,my]
                    last = drawRect(startPos[0],startPos[1],endPos[0],endPos[1],2,(255,0,0))
                ##SECTION END - Same function as previously mentioned
                if status['mbup'] == 1 and dragging:
                    centerx = startPos[0]+(endPos[0]-startPos[0])/2#x center of selection rectangle
                    centery = startPos[1]+(endPos[1]-startPos[1])/2#y center of selection rectangle
                    a1,b1,c1,d1 = last#Rect() values for the selection rectangle
                    dragging = False
                    rdone = True#Flag to see if user is done selection of rectangle
            if rdone:#If user is done selecting rectangle, start rotate process
                if status['mbdown'] == 1:
                    startPos = [mx,my]#Get start position
                    dragging = True
                if dragging:
                    endPos = [mx,my]#current mouse position
                    dx = endPos[0]-centerx#x distance from endPos to center
                    dy = endPos[1]-centery#y distance from endPos to center
                    degs = math.degrees(math.atan2(dx,dy))-90#Get number of degrees to rotate
                    tempCopy = screen.copy()
                    rsurf = tempCopy.subsurface(Rect(a1,b1,c1,d1))#Subsurface the area selected to rotate
                    rsurf.set_colorkey(0)#Make the background (black) transparent
                    rsurf = transform.rotate(rsurf,degs)#Rotate by the number of degrees
                    draw.rect(screen,(0,0,0),(a1,b1,c1,d1),0)#Draw a black rectangle where 
                    rotated = screen.blit(rsurf,(centerx-rsurf.get_width()//2,centery-rsurf.get_height()//2))
                if status['mbup'] == 1 and dragging:
                    copy_list.append(screen.copy())
                    dragging = False
                    rdone = False
                    redo = []#Empty redo list
    elif mode == 'moveTool':
        if first_time:#If a selection rectangle hasn't been drawn yet, take a screen copy
            no_rect = screen.copy()
            first_time = False
        if drawSpace.collidepoint(mx,my):
            if not rdone:#SECTION BEGIN
                if status['mbdown'] == 1 and not rdone:
                    startPos = [mx,my]
                    dragging=True
                if dragging:
                    endPos = [mx,my]
                    last = drawRect(startPos[0],startPos[1],endPos[0],endPos[1],2,(255,0,0))
                if status['mbup'] == 1 and dragging:
                    centerx = startPos[0]+(endPos[0]-startPos[0])/2
                    centery = startPos[1]+(endPos[1]-startPos[1])/2
                    a1,b1,c1,d1 = last
                    dragging = False
                    rdone = True
                #SECTION END -- Get selection rectangle
            if rdone:
                screen.blit(no_rect,(0,0))
                if status['mbdown'] == 1:
                    startPos = [mx,my]#Get start position
                    dragging = True
                if dragging:
                    endPos = [mx,my]
                    tempCopy = screen.copy()
                    rsurf = tempCopy.subsurface(Rect(a1,b1,c1,d1))#Subsurface selection rectangle
                    rsurf.set_colorkey(0)#Make background transparent
                    draw.rect(screen,(0,0,0),(a1,b1,c1,d1),0)#Draw black rectangle over selection area
                    screen.blit(rsurf,(mx-c1//2,my-d1//2))#Blit selected area with center at mx,my
                if status['mbup'] == 1 and dragging:
                    copy_list.append(screen.copy())
                    dragging = False##
                    rdone = False#Reset variables
                    first_time = True##
                    redo = [] #Empty redo list
    elif mode == 'textTool':
        avenir = font.Font('avenir.ttf', 18+shape_size)#Load font with adjustable size based on shape_size
        cursor_counter += 1#Used to not draw cursor every iteration
        if status['mbdown'] == 1:
            typing = True
            pos = (mx,my)#Get location of mouse
        if typing:
            txt = avenir.render(msg, True, color)#Render text got from event loop
            screen.blit(txt, pos)
            if cursor_counter // 50 % 2 == 1:#Only draw the cursor every so often
                cursor_pos = (pos[0]+txt.get_width()+2,pos[1]+3)#Cursor position
                draw.rect(screen, (255,0,0), (cursor_pos[0],cursor_pos[1],2,txt.get_height()))#Draw cursor
        if request_exit:#User requests end to typing
            if cursor_counter // 50 % 2 == 0:#If cursor is not blitted, copy the screen
                copy_list.append(screen.copy())
                redo = []#Empty redo list
                typing = False      #
                request_exit = False# Reset variables
                msg = ''            #
    
    press = key.get_pressed()#Get pressed keys
    if press[control_modifier] == 1 and press[K_z] == 1 and press[shift_key] != 1 and only_undo_once:#If Modifier-Z is pressed, undo
        if len(copy_list) > 0:
            popped = copy_list.pop()
            redo.append(popped)
            try:
                screen.blit(copy_list[-1],(0,0))
            except:
                screen.blit(base,(0,0))#If list is empty, just blit an empty screen
            old_c = len(copy_list)
    elif press[control_modifier] == 1 and press[shift_key] == 1 and press[K_z] == 1 and only_undo_once:#If Shift-Modifier-Z is pressed, redo
        if len(redo) > 0:
            copy_list.append(redo.pop())
            screen.blit(copy_list[-1],(0,0))
            old_r = len(redo)
    display.flip()
quit()
