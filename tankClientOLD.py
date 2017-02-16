from tkinter import *
import math
###############################################
#Multiplayer Server Message Handling (Taken from Rohans examples)
###############################################
import socket
import threading
from queue import Queue

HOST = "128.237.162.243"
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg): #handles msgs from server
	server.setblocking(1)
	msg = ""
	command = ""
	while True:
		msg += server.recv(10).decode("UTF-8")
		command = msg.split("\n")
		while (len(command) > 1):
			readyMsg = command[0]
			print(readyMsg)
			msg = "\n".join(command[1:])
			serverMsg.put(readyMsg)
			command = msg.split("\n")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
###############################################
#Helpers
################################################
#really stupid helper functions
def degreeToRad(deg):
	degreesInCircle = 360
	return deg*math.pi*2/degreesInCircle
def db(*whatever):
	debug = False
	if debug:
		print(*whatever)
def slope(x0,y0,x1,y1):
	try: return (y1-y0)/(x1-x0)
	except: return 1000000000

#useful important helper functions
def createTank(data, category,x=None,y=None,ang=None):#returns tank object based on type
	if category=="player":
		col1 = data.playerColors[0]
		col2 = data.playerColors[1]
	if category=="enemy":
		col1 = data.enemyColors[0]
		col2 = data.enemyColors[1]
	if category=="ally":
		pass
	if ang==None:
		ang = degreeToRad(0)
	if x==None:
		x = data.width//2
	if y==None:
		y = data.height//2
	return Tank(x,y,col1,col2,ang,data.width,data.height)
def rectangleVerts(x,y,sizeX,sizeY,theta=0): #returns verts of rect at ang thta
	verts = []
	diag = ((sizeX/2)**2+(sizeY/2)**2)**.5
	theta += math.atan2(sizeY,sizeX) #calc theta for 1st point
	verts.append(x+diag*math.cos(theta)) #vert1x
	verts.append(y-diag*math.sin(theta)) #vert1y
	theta+=2*(math.atan2(sizeX,sizeY))#add to theta for 2nd point
	verts.append(x+diag*math.cos(theta))  #vert2x
	verts.append(y-diag*math.sin(theta)) #vert2y
	theta+=2*(math.atan2(sizeY,sizeX))#add to theta for 3rd point
	verts.append(x+diag*math.cos(theta))  #vert3x
	verts.append(y-diag*math.sin(theta)) #vert3y
	theta+=2*(math.atan2(sizeX,sizeY))#add to theta for 4th point
	verts.append(x+diag*math.cos(theta))  #vert4x
	verts.append(y-diag*math.sin(theta))  #vert4y
	return verts
def circleLineCollision(x0,y0,x1,y1,x2,y2,radius):
	m = slope(x1,y1,x2,y2)
	a = m
	b = -1
	c = y1-m*x1
	dist = (abs(a*x0+b*y0+c))/((a**2+b**2)**.5) #perp dist from line to point
	#formula derived using vector projections
	db(dist)
	x = (b*(b*x0-a*y0)-a*c)/(a**2+b**2) #x cord of closest perp point
	db(x1,x,x2)
	return (dist<radius) and min(x1,x2)<=x<=max(x1,x2)
###############################################
## Objects
###############################################
class Tank(object):
	def __init__(self, x, y, color1, color2, angle,canvasWidth, canvasHeight):
		self.x = x
		self.y = y
		self.sizeX = 50
		self.sizeY = 50
		self.treadSizeY = 0.15*self.sizeY
		self.treadSizeX = 0.1*self.sizeX
		self.nozzSizeY = 0.3*self.sizeY
		self.nozzSizeX = 0.55*self.sizeX
		self.tankColor = color1
		self.nozzColor = color2
		self.rotSpeed = 2
		self.moveSpeed = 2
		self.canvasWidth = canvasWidth
		self.canvasHeight = canvasHeight
		self.theta = angle
	def draw(self, canvas):
		self.tankVerts = rectangleVerts(self.x,self.y,self.sizeX,self.sizeY,self.theta)
		canvas.create_polygon(self.tankVerts[0],self.tankVerts[1],self.tankVerts[2],
							self.tankVerts[3],self.tankVerts[4],self.tankVerts[5],self.tankVerts[6],
							self.tankVerts[7],fill = self.tankColor) #draw body of tank
		nozzX = (self.tankVerts[0]+self.tankVerts[6])//2 #avg 1st & 4th tankVerts X
		nozzY = (self.tankVerts[1]+self.tankVerts[7])//2 #avg 1st & 4th tankVerts Y
		self.nozzVerts = rectangleVerts(nozzX, nozzY, self.nozzSizeX, self.nozzSizeY, self.theta)
		canvas.create_polygon(self.nozzVerts[0],self.nozzVerts[1],self.nozzVerts[2],
							self.nozzVerts[3],self.nozzVerts[4],self.nozzVerts[5],self.nozzVerts[6],
							self.nozzVerts[7],fill = self.nozzColor) #draw body of tank
		radius = min(self.sizeX,self.sizeY)*0.35
		canvas.create_oval(self.x-radius,self.y-radius, self.x+radius, self.y+radius, fill=self.nozzColor, width = 0)
	def rotateLeft(self):
		self.theta += degreeToRad(self.rotSpeed)
	def rotateRight(self):
		self.theta -= degreeToRad(self.rotSpeed)
	def moveForward(self):
		self.x+=self.moveSpeed*math.cos(self.theta)
		self.y-=self.moveSpeed*math.sin(self.theta)
	def moveBackward(self):
		self.x-=self.moveSpeed*math.cos(self.theta)
		self.y+=self.moveSpeed*math.sin(self.theta)
	def shoot(self,data):
		cx =(self.nozzVerts[0]+self.nozzVerts[6])//2
		cy = (self.nozzVerts[1]+self.nozzVerts[7])//2 #avg of 1,4 tankVerts
		bullet = Bullet(cx,cy,self.nozzColor,self.nozzSizeY/2,self.theta,
						self.canvasHeight,self.canvasWidth)
		data.bullets.append(bullet)
	def __repr__(self):
		return "Tank(x=%d,y=%d,angle=%f" %(self.x,self.y,self.theta)
class Bullet(object):
	def __init__(self,x,y,color,radius,angle,canvasHeight,canvasWidth):
		self.x = x
		self.y = y
		self.color = color
		self.radius = radius
		self.speed = 5
		self.theta = angle
		self.canvasHeight = canvasHeight
		self.canvasWidth = canvasWidth
		self.bounces = 0
		self.maxBounces = 8
		self.separate = False
	def draw(self,canvas):
		x0,y0 = self.x-self.radius, self.y-self.radius
		x1,y1 = self.x+self.radius, self.y+self.radius
		canvas.create_oval(x0,y0,x1,y1,fill=self.color)
	def move(self):
		self.x+=self.speed*math.cos(self.theta)
		self.y-=self.speed*math.sin(self.theta)
	def borderCollision(self):
		if (self.x+self.radius>=self.canvasWidth or self.x-self.radius<=0):
			self.theta = math.pi - self.theta
			self.bounces +=1
		if (self.y-self.radius<=0 or self.y+self.radius>=self.canvasHeight):
			self.theta = 2*math.pi - self.theta
			self.bounces+=1
	def killBullet(self):
		if self.bounces>=self.maxBounces:
			return True
	def tankCollision(self, tank):
		for vert in range(0,8,2): #4 points in a rectangle
			if circleLineCollision(self.x,self.y,
								  tank.tankVerts[vert-2],tank.tankVerts[vert-1],
								  tank.tankVerts[vert],tank.tankVerts[vert+1],
								  self.radius):
										return True
		return False
	def bulletCollision(self, bullet):
		if (((self.x-bullet.x)**2+(self.y-bullet.y)**2)**.5)<2*self.radius:
			return True
################################################
##	Model
################################################
def init(data):
	data.playerColors = ["blue","green"]
	data.enemyColors = ["red", "orange"]
	data.plTank = createTank(data, "player")
	data.enemyTanks = []
	data.allyTanks = []
	data.bullets = []
	data.walls = []
	data.minPlayers = 4
	data.gameOver = False
	data.win = False
	data.start = False
	data.splash = True
################################################
## Control
################################################
def keyPressed(event, data):
	if not data.start: return
	if (event.keysym == "Left"):
		data.plTank.rotateLeft()
		msg = "left:\n"
		db("sending:", msg)
		data.server.send(msg.encode())
	if (event.keysym == "Right"):
		data.plTank.rotateRight()
		msg = "right:\n"
		db("sending:", msg)
		data.server.send(msg.encode())
	if (event.keysym == "Up"):
		data.plTank.moveForward()
		msg = "forward:\n"
		db("sending:", msg)
		data.server.send(msg.encode())
	if (event.keysym == "Down"):
		data.plTank.moveBackward()
		msg = "backward:\n"
		db("sending:", msg)
		data.server.send(msg.encode())
	if (event.keysym == "space"):
		data.plTank.shoot(data)
		msg = "shoot:\n"
		db("sending:", msg)
		data.server.send(msg.encode())

def mousePressed(event, data):
	pass
def timerFired(data):
	if (serverMsg.qsize() > 0):
		msg = serverMsg.get(False)
		# try:
		db("received: ", msg)
		msg = msg.split(":")
		action = msg[0]
		if action == "newPlayer":
			plID = int(msg[1])
			db("newPlayer_%d has joined" %plID)
			data.enemyTanks.append([plID,createTank(data,"enemy")])
			db(data.enemyTanks)
		elif action == "forward":
			plID = int(msg[1])
			db("Player_%d moved forward" %plID)
			for enemyTank in data.enemyTanks:
				if enemyTank[0] == plID:
					enemyTank[1].moveForward()
					break
		elif action == "backward":
			plID = int(msg[1])
			db("Player_%d moved backward" %plID)
			for enemyTank in data.enemyTanks:
				if enemyTank[0] == plID:
					enemyTank[1].moveBackward()
					break
		elif action == "left":
			plID = int(msg[1])
			db("Player_%d rotated Left" %plID)
			for enemyTank in data.enemyTanks:
				if enemyTank[0] == plID:
					enemyTank[1].rotateLeft()
					break
		elif action == "right":
			plID = int(msg[1])
			db("Player_%d rotated Right" %plID)
			for enemyTank in data.enemyTanks:
				if enemyTank[0] == plID:
					enemyTank[1].rotateRight()
					break
		elif action == "shoot":
			plID = int(msg[1])
			db("Player_%d shot!" %plID)
			for enemyTank in data.enemyTanks:
				if enemyTank[0] == plID:
					enemyTank[1].shoot(data)
					break
		# except:
		# 	db("failed")
		serverMsg.task_done()
	if len(data.enemyTanks)>=data.minPlayers-1:
		data.start = True
	if not data.start: return #put game stuff below this
	for bullet in data.bullets:
		bullet.move()
		bullet.borderCollision()
		if bullet.tankCollision(data.plTank):
			db("Collision: self")
			data.gameOver = True
			data.bullets.remove(bullet)
			continue
		for tank in data.enemyTanks:
			if bullet.tankCollision(tank[1]):
				data.enemyTanks.remove(tank)
				data.bullets.remove(bullet)
				break
		if bullet.killBullet():
			data.bullets.remove(bullet)
			continue
		for bullet2 in data.bullets:
			if bullet==bullet2: continue
			if bullet.bulletCollision(bullet2):
				data.bullets.remove(bullet)
				data.bullets.remove(bullet2)
				break
	if len(data.enemyTanks)==0:
		if data.start == True:
			data.win = True
			data.gameOver = True

#################################################
## View
#################################################
def drawBorder(canvas, data):
	canvas.create_rectangle(2,2,data.width,data.height,width=2)

def drawGameOver(canvas, data):
	if data.win:
		txt = "You\nWin!"
		col = "green"
	else:
		txt = "You\nLose"
		col = "red"
	canvas.create_text(data.width//2,data.height//2,text=txt,
						font = "Times 40 bold", fill = col)

def drawSplash(canvas, data):
	canvas.create_rectangle(0,0,data.width,data.height,fill="light pink")
	remPlyrs = data.minPlayers-1-len(data.enemyTanks)
	canvas.create_text(data.width/2, data.height/4,
						text = "Waiting for %d \n more Players" %remPlyrs,
						font = "Arial 40 bold")
	inst = """Up and Down to move forwards and backwards\nLeft and Right to rotate left and right\nSpace to shoot\nDestroy everyone else to win!"""
	canvas.create_text(data.width/2, 3*data.height/4,
						text=inst, font = "Arial 10")

def redrawAll(canvas, data):
	if not data.start:
		drawSplash(canvas, data)
		return
	drawBorder(canvas,data)
	for bullet in data.bullets:
		bullet.draw(canvas)
	for enemyTank in data.enemyTanks:
		enemyTank[1].draw(canvas)
	for allyTank in data.allyTanks:
		allyTank[1].draw(canvas)
	if not data.gameOver or data.win:
		data.plTank.draw(canvas)
	if data.gameOver:
		drawGameOver(canvas,data)

##################################################
##Run Function (adapted from socket example)
##################################################
def run(width, height, serverMsg=None, server=None):
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
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 10 # milliseconds
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

run(400, 400, serverMsg, server)