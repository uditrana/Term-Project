from tkinter import *
import math

###############################################
## Objects
###############################################
class Tank(object):
	def __init__(self, x, y, sizeX, sizeY, color1, color2, angle, rotSpeed,
				 moveSpeed,canvasWidth, canvasHeight):
		self.x = x
		self.y = y
		self.sizeX = sizeX
		self.sizeY = sizeY
		self.treadSizeY = 0.15*self.sizeY
		self.treadSizeX = 0.1*self.sizeX
		self.nozzleSizeY = 0.2*self.sizeY
		self.nozzleSizeX = 0.25*self.sizeX
		self.diag = ((self.sizeX/2)**2+(self.sizeY/2)**2)**.5
		self.tankColor = color1
		self.nozzleColor = color2
		self.canvasHeight = canvasHeight
		self.rotSpeed = rotSpeed
		self.moveSpeed = moveSpeed
		self.canvasWidth = canvasWidth
		self.angle = angle #degree val for angle
		self.theta = (self.angle*math.pi)/180 #rad val for angle
	def draw(self, canvas):
		theta = self.theta #temp var for theta
		verts = []
		theta += math.atan2(self.sizeY,self.sizeX) #calc theta for 1st point
		verts.append(self.x+self.diag*math.cos(theta)) #vert1x
		verts.append(self.y-self.diag*math.sin(theta)) #vert1y
		theta+=2*(math.atan2(self.sizeX,self.sizeY))#add to theta for 2nd point
		verts.append(self.x+self.diag*math.cos(theta))  #vert2x
		verts.append(self.y-self.diag*math.sin(theta)) #vert2y
		theta+=2*(math.atan2(self.sizeY,self.sizeX))#add to theta for 3rd point
		verts.append(self.x+self.diag*math.cos(theta))  #vert3x
		verts.append(self.y-self.diag*math.sin(theta)) #vert3y
		theta+=2*(math.atan2(self.sizeX,self.sizeY))#add to theta for 4th point
		verts.append(self.x+self.diag*math.cos(theta))  #vert4x
		verts.append(self.y-self.diag*math.sin(theta))  #vert4y
		# canvas.create_rectangle(verts[2]-self.treadSizeX,
		# 						verts[3]-self.treadSizeY,
		# 						verts[0]+self.treadSizeX,
		# 						verts[1]+self.treadSizeY,
		# 						fill = "black") #Tank Left Treads
		# canvas.create_rectangle(verts[4]-self.treadSizeX,
		# 						verts[5]-self.treadSizeY,
		# 						verts[6]+self.treadSizeX,
		# 						verts[7]+self.treadSizeY,
		# 						fill = "black") #Tank Right Treads
		canvas.create_polygon(verts[0],verts[1],verts[2],verts[3],
							  verts[4],verts[5],verts[6],verts[7],
							  fill = self.tankColor) #draw body of tank
		cx,cy = (verts[0]+verts[6])//2, (verts[1]+verts[7])//2 #avg of 1,4 verts
		r = 10 #random test magic val
		canvas.create_oval(cx-r,cy-r,cx+r,cy+r, fill = self.nozzleColor) #temp nozzle
	def rotateLeft(self):
		self.angle += self.rotSpeed
		self.theta = (self.angle*math.pi)/180
	def rotateRight(self):
		self.angle -= self.rotSpeed
		self.theta = (self.angle*math.pi)/180
	def moveForward(self):
		self.x+=self.moveSpeed*math.cos(self.theta)
		self.y-=self.moveSpeed*math.sin(self.theta)
	def moveBackward(self):
		self.x-=self.moveSpeed*math.cos(self.theta)
		self.y+=self.moveSpeed*math.sin(self.theta)
	def shoot(self,data):
		bullet = Bullet(self.x,self.y,self.nozzleColor,10,5,self.angle,
						self.canvasHeight,self.canvasWidth)
		data.bullets.append(bullet)

class Bullet(object):
	def __init__(self,x,y,color,radius,speed,angle,canvasHeight,canvasWidth):
		self.x = x
		self.y = y
		self.color = color
		self.radius = radius
		self.speed = speed
		self.angle = angle
		self.theta = (self.angle*math.pi)/180 #rad val for angle
		self.canvasHeight = canvasHeight
		self.canvasWidth = canvasWidth
	def draw(self,canvas):
		x0,y0 = self.x-self.radius, self.y-self.radius
		x1,y1 = self.x+self.radius, self.y+self.radius
		canvas.create_oval(x0,y0,x1,y1,fill=self.color)
	def move(self):
		self.x+=self.speed*math.cos(self.theta)
		self.y-=self.speed*math.sin(self.theta)


################################################
##	Model
################################################
def init(data):
	data.x, data.y = data.width//2, data.height//2
	data.moveSpeed = 5
	data.rotateSpeed = 5
	data.tankSizeX,data.tankSizeY = 100,80
	data.angle = 0
	data.tank = Tank(data.x,data.y,data.tankSizeX,data.tankSizeY,"green","red",
						data.angle,data.rotateSpeed,data.moveSpeed,
						data.width, data.height)
	data.bullets = []
	data.gameOver = False
################################################
## Control
################################################
def keyPressed(event, data):
    if (event.keysym == "Left"):
        data.tank.rotateLeft()
    if (event.keysym == "Right"):
        data.tank.rotateRight()
    if (event.keysym == "Up"):
    	data.tank.moveForward()
    if (event.keysym == "Down"):
    	data.tank.moveBackward()
    if (event.keysym == "space"):
    	data.tank.shoot(data)

def mousePressed(event, data):
    pass
def timerFired(data):
    for bullet in data.bullets:
    	bullet.move()

################################################
## View
################################################
def redrawAll(canvas, data):
    if (not data.gameOver):
        data.tank.draw(canvas)
        for bullet in data.bullets:
        	bullet.draw(canvas)

##################################################
##Run Function
##################################################
def run(width=300, height=300): #Run function adapted from notes
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 50 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800, 800)