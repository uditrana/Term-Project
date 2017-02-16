from tkinter import *
import math
###############################################
#Multiplayer Server Message Handling (Taken from Rohans examples)
###############################################
import socket
import threading
from queue import Queue

HOST = "103.211.41.135"
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
#Helpers (Written by me)
################################################
#really brainless helper functions
def degreeToRad(deg):
	degreesInCircle = 360
	return deg*math.pi*2/degreesInCircle
def db(*whatever):
	debug = True
	if debug:
		print(*whatever)
def slope(x0,y0,x1,y1):
	try: return (y1-y0)/(x1-x0)
	except: return 1000000000

#useful important helper functions
def createTank(data, category,x=None,y=None,theta=None):#returns tank object based on type
	if category=="player":
		col1 = data.playerColors[0]
		col2 = data.playerColors[1]
	if category=="enemy":
		col1 = data.enemyColors[0]
		col2 = data.enemyColors[1]
	if category=="ally":
		pass
	if theta==None:
		theta = degreeToRad(0)
	if x==None:
		x = data.width//2
	if y==None:
		y = data.height//2
	return Tank(x,y,col1,col2,theta)
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
	# db(dist)
	x = (b*(b*x0-a*y0)-a*c)/(a**2+b**2) #x cord of closest perp point
	# db(x1,x,x2)
	return (dist<radius) and min(x1,x2)<=x<=max(x1,x2)
def lineLineCollision(x0,y0,x1,y1):
	pass
def circleCircleCollision(x0,y0,x1,y1,r1,r2):
	if (((x1-x0)**2+(y1-y0)**2)**.5)<(r1+r2):
		return True
###############################################
## Objects (Written by me)
###############################################
class Tank(object):
	def __init__(self, x, y, color1, color2, angle):
		self.x = x
		self.y = y
		self.sizeX = 35
		self.sizeY = 30
		self.treadSizeY = 0.15*self.sizeY
		self.treadSizeX = 0.1*self.sizeX
		self.nozzSizeY = 0.3*self.sizeY
		self.nozzSizeX = 0.55*self.sizeX
		self.circRadius = min(self.sizeX,self.sizeY)*0.35
		self.tankColor = color1
		self.nozzColor = color2
		self.rotSpeed = 3
		self.moveSpeed = 3
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
							self.nozzVerts[7],fill = self.nozzColor) #draw nozzle of tank
		canvas.create_oval(self.x-self.circRadius,self.y-self.circRadius,
						   self.x+self.circRadius,self.y+self.circRadius,
						   fill=self.nozzColor, width = 0)
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
		bullet = Bullet(cx,cy,self.nozzColor,self.nozzSizeY/2,self.theta,)
		data.bullets.append(bullet)
	def __repr__(self):
		return "Tank(x=%d,y=%d,angle=%f" %(self.x,self.y,self.theta)
class Bullet(object):
	def __init__(self,x,y,color,radius,angle):
		self.x = x
		self.y = y
		self.color = color
		self.radius = radius
		self.speed = 5
		self.theta = angle
		self.bounces = 0
		self.maxBounces = 10
		self.separate = False
	def draw(self,canvas):
		x0,y0 = self.x-self.radius, self.y-self.radius
		x1,y1 = self.x+self.radius, self.y+self.radius
		canvas.create_oval(x0,y0,x1,y1,fill=self.color)
	def move(self):
		self.x+=self.speed*math.cos(self.theta)
		self.y-=self.speed*math.sin(self.theta)
	def wallCollision(self, wall):
		if (self.x+self.radius>=wall.x0 and self.x<wall.x0 and wall.y0<self.y+self.radius<wall.y1):
			self.theta = math.pi - self.theta
			self.bounces+=1
		if (self.x-self.radius<=wall.x1 and self.x>wall.x1 and wall.y0<self.y-self.radius<wall.y1):
			self.theta = math.pi - self.theta
			self.bounces+=1
		if (self.y+self.radius>=wall.y0 and self.y<wall.y0 and wall.x0<self.x+self.radius<wall.x1):
			self.theta = 2*math.pi - self.theta
			self.bounces+=1
		if (self.y-self.radius<=wall.y1 and self.y>wall.y1 and wall.x0<self.x-self.radius<wall.x1):
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
		if circleCircleCollision(self.x,self.y,bullet.x,bullet.y,self.radius,bullet.radius):
			return True
class Wall(object):
	def __init__(self, x, y, size=None, thick=None):
		self.x = x
		self.y = y
		if size==None:
			self.size = 100 #preferably even
		else:
			self.size = size
		if thick==None:
			self.thick = 10 #preferably even
		else:
			self.thick = thick
	def draw(self,canvas):
		canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1,fill="black", width=0)
	def checkInside(self,x,y):
		return self.x0<x<self.x1 and self.y0<y<self.y1
	def __repr__(self):
		return str(self.x)+","+str(self.y)
class horizantalWall(Wall):
	def __init__(self, x, y, size = None, thick=None):
		super().__init__(x,y,size,thick)
		self.x0 = self.x - self.size/2
		self.x1 = self.x + self.size/2
		self.y0 = self.y - self.thick/2
		self.y1 = self.y + self.thick/2
class verticalWall(Wall):
	def __init__(self, x, y, size = None, thick=None):
		super().__init__(x,y,size,thick)
		self.x0 = self.x - self.thick/2
		self.x1 = self.x + self.thick/2
		self.y0 = self.y - self.size/2
		self.y1 = self.y + self.size/2
class Spawn(Tank):
	def __init__(self, x,y, ang = 0):
		super().__init__(x,y,"black","gray",degreeToRad(ang))
		self.ang = ang
	def rotate(self):
		self.theta += degreeToRad(90)
		self.ang += 90
		return self
	def getAngle(self):
		return self.ang
	def checkInside(self,x,y):
		x0,x1 = self.x-self.circRadius,self.x+self.circRadius
		y0,y1 = self.y-self.circRadius,self.y+self.circRadius
		return x0<x<x1 and y0<y<y1
################################################
##	Model (written by me)
################################################
def init(data):
	data.playerColors = ["blue","green"]
	data.enemyColors = ["red", "orange"]
	data.plID = -1
	data.plTank = createTank(data, "player",50,50,degreeToRad(180))
	data.pressedKeys = []
	data.otherPressedKeys = dict()
	data.enemyTanks = []
	data.allyTanks = []
	data.bullets = []
	data.walls = []
	data.spawns = []
	# data.cursorX = 0
	# data.cursorY = 0
	data.margin = 4
	data.walls.append(verticalWall(data.margin,data.height/2,data.height))
	data.walls.append(verticalWall(data.width,data.height/2,data.height))
	data.walls.append(horizantalWall(data.width/2,data.margin,data.width))
	data.walls.append(horizantalWall(data.width/2,data.height,data.width))
	data.wallType = True #True is vert, false is horizantal
	data.viewObjType = True #True is wall, false is spawn
	data.viewObj = None
	data.minPlayers = 4
	data.gameOver = False
	data.ready = False
	data.win = False
	data.start = False #game started mode
	data.maze = False #in maze building mode...
	data.splash = True #in splash screen
################################################
## Control (written by me)
################################################
def keyPressed(event, data):
	if (event.keysym == "r"):
		if data.maze:
			data.ready = not data.ready
		if data.ready:
			msg = "ready:\n"
		else: msg = "unready:\n"
		data.server.send(msg.encode())
	if data.maze:
		if event.keysym == "q":
			data.viewObjType = not data.viewObjType
			if data.viewObjType == False:
				data.viewObj = Spawn(event.x,event.y)
			if data.viewObjType == True:
				if data.wallType == True:
					data.viewObj = verticalWall(event.x,event.y)
				if data.wallType == False:
					data.viewObj = horizantalWall(event.x,event.y)
		if event.keysym == "space":
			if data.viewObjType==True:
				data.wallType = not data.wallType
				if data.wallType == True:
					data.viewObj = verticalWall(event.x,event.y)
				if data.wallType == False:
					data.viewObj = horizantalWall(event.x,event.y)
			if data.viewObjType == False:
				data.viewObj.rotate()
		if event.keysym == "h":
			data.splash = True
			data.maze = False

		return
	# if (event.keysym not in data.pressedKeys):
	# 	msg = "keyPressed:" + event.keysym +":\n"
	if data.start:
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

def doKeys(key, tank): #these are the functions that need to work while held down
	if (key == "Left"):
		tank.rotateLeft()
	if (key == "Right"):
		tank.rotateRight()
	if (key == "Up"):
		tank.moveForward()
	if (key == "Down"):
		tank.moveBackward()

def keyReleased(event, data): pass
# 	if (event.keysym in data.pressedKeys):
# 		msg = "keyReleased:" + event.keysym +":\n"
# 		db("sending:", msg)
# 		data.server.send(msg.encode())
# 		data.pressedKeys.remove(event.keysym) 	
def mouse1Pressed(event, data):
	if data.maze:
		if data.viewObjType==True:
			if data.wallType == True:
				data.walls.append(data.viewObj)
				msg = "vertWall:%d:%d:\n" %(event.x,event.y)
				data.server.send(msg.encode())
			if data.wallType == False:
				data.walls.append(data.viewObj)
				msg = "horWall:%d:%d:\n" %(event.x,event.y)
				data.server.send(msg.encode())
		if data.viewObjType==False:
			data.spawns.append(data.viewObj)
			msg = "spawn:%d:%d:%d:\n" %(event.x,event.y,data.viewObj.getAngle())
			data.server.send(msg.encode())
	if data.splash:
		if 0<event.x<data.width and 0<event.y<data.height:
			data.splash=False
			data.maze = True

def mouse3Pressed(event, data):
	if data.maze:
		for wall in data.walls:
			if wall.checkInside(event.x,event.y):
				data.walls.remove(wall)
				msg = "removeWall:%d:%d:\n" %(wall.x,wall.y)
				data.server.send(msg.encode())	
				break
		for spawn in data.spawns:
			if spawn.checkInside(event.x,event.y):
				data.spawns.remove(spawn)
				msg = "removeSpawn:%d:%d:\n" %(spawn.x,spawn.y)
				data.server.send(msg.encode())
				break
def mouseMotion(event,data):
	if data.maze:
		if data.viewObjType == False:
				data.viewObj = Spawn(event.x,event.y,data.viewObj.getAngle())
		if data.viewObjType == True:
			if data.wallType == True:
				data.viewObj = verticalWall(event.x,event.y)
			if data.wallType == False:
				data.viewObj = horizantalWall(event.x,event.y)
		# if data.wallType == True:
		# 	data.viewObj = verticalWall(event.x,event.y)
		# if data.wallType == False:
		# 	data.viewObj = horizantalWall(event.x,event.y)
		# msg = "cursor:%d:%d:\n" %(event.x, event.y)
		# data.server.send(msg.encode())

def timerFired(data):
	if (serverMsg.qsize() > 0):
		msg = serverMsg.get(False)
		msg = msg.split(":")
		action = msg[0]
		print (action)
		if action == "vertWall":
			x,y = int(msg[1]),int(msg[2])
			data.walls.append(verticalWall(x,y))
		elif action == "horWall":
			x,y = int(msg[1]),int(msg[2])
			data.walls.append(horizantalWall(x,y))
		elif action == "removeWall":
			x,y = int(msg[1]),int(msg[2])
			for wall in data.walls:
				if wall.x==x and wall.y==y:
					data.walls.remove(wall)
					break
		elif action == "spawn":
			x,y,ang = int(msg[1]),int(msg[2]), int(msg[3])
			data.spawns.append(Spawn(x,y,ang))
		elif action == "removeSpawn":
			x,y = int(msg[1]),int(msg[2])
			for spawn in data.spawns:
				if spawn.x==x and spawn.y==y:
					data.spawns.remove(spawn)
					break
		elif action == "start":
			data.start = True
			data.maze =  False
			data.splash = False
			data.ready = False
			data.timerDelay = 10
		elif action == "newPlayer":
			plID = int(msg[1])
			x,y,ang = int(msg[2]), int(msg[3]), int(msg[4])
			db("newPlayer_%d has joined" %plID)
			data.enemyTanks.append([plID,createTank(data,"enemy",x,y,degreeToRad(ang))])
			# data.otherPressedKeys[plID]=[]
			db(data.enemyTanks)
		elif action == "player":
			data.plID = int(msg[1])
			db ("you have joined")
			x,y,ang = int(msg[2]), int(msg[3]), int(msg[4])
			data.plTank = createTank(data, "player",x,y,degreeToRad(ang))
			db(data.plTank)
		elif action == "keyPressed":
			dir = msg[1]
			plID = int(msg[2])
			data.otherPressedKeys[plID].append(dir)
		elif action == "keyReleased":
			dir = msg[1]
			plID = int(msg[2])
			data.otherPressedKeys[plID].remove(dir)
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
		elif action == "cursor":
			x,y = int(msg[1]),int(msg[2])
			data.cursorX = x
			data.cursorY = y
		serverMsg.task_done()
	if not data.start: return #put game stuff below this
	# for key in data.pressedKeys:
	# 	doKeys(key, data.plTank)
	# for enemyTank in data.enemyTanks:
	# 	for key in data.otherPressedKeys[enemyTank[0]]:
	# 		print (enemyTank, data.otherPressedKeys[enemyTank[0]])
	# 		doKeys(key, enemyTank[1])
	for bullet in data.bullets: #run all bullet motion and collisions
		bullet.move()
		for wall in data.walls:
			bullet.wallCollision(wall)
		if bullet.tankCollision(data.plTank):
			db("Collision: self")
			data.gameOver = True
			data.plTank = createTank(data, "player",5000,5000,degreeToRad(180))
			data.bullets.remove(bullet)
			continue
		for tank in data.enemyTanks:
			if bullet.tankCollision(tank[1]):
				db("Collision: enemy")
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
		if data.gameOver == False:
			# data.start=False
			data.win = True
			data.gameOver = True

#################################################
## View (written by me)
#################################################
def drawGameOver(canvas, data):
	if data.win:
		txt = "You\nWin!"
		col1 = "green"
		col2 = "pink"
	else:
		txt = "You\nLose"
		col1 = "red"
		col2 = "gray"
	canvas.create_text(data.width//2-200, )
	canvas.create_text(data.width//2,data.height//2,text=txt,
						font = "Times 40 bold", fill = col1)

def drawSplash(canvas, data):
	canvas.create_rectangle(0,0,data.width,data.height,fill="light pink")
	remPlyrs = data.minPlayers-1-len(data.enemyTanks)
	canvas.create_text(data.width/2, data.height/4,
						text = "TANKS",
						font = "Helvetica 40 bold")
	instruc ="""Build a map with other players\nLMB to place wall, RMB to remove wall, space to rotate\nHit 'r' when ready to play map!\nUse arrow keys and space bar to destroy everyone else\nhit 'h' to return to help\nclick to continue to level-builder"""
	canvas.create_text(data.width/2, 3*data.height/4,
						text=instruc, font = "Arial 15", justify = "center")

def drawCursor(canvas, data):
	canvas.create_oval(data.cursorX-10,data.cursorY-10,data.cursorX+10,data.cursorY+10,fill="red")

def drawReady(canvas, data):
	canvas.create_rectangle(data.width//2-150, data.height//2-50, data.width//2+150, data.height//2+50,fill="pink")
	canvas.create_text(data.width//2,data.height//2,text="READY",font = "Times 30 bold", fill = "green")

def redrawAll(canvas, data):
	if data.splash:
		drawSplash(canvas, data)
	if data.maze:
		for wall in data.walls:
			wall.draw(canvas)
		for spawn in data.spawns:
			spawn.draw(canvas)
		if data.viewObj != None:
			data.viewObj.draw(canvas)
		# drawCursor(canvas,data)
	if data.ready and data.maze:
		drawReady(canvas,data)
	if not data.start:
		return
	for bullet in data.bullets:
		bullet.draw(canvas)
	for enemyTank in data.enemyTanks:
		enemyTank[1].draw(canvas)
	if data.plTank!= None:
		data.plTank.draw(canvas)
	for wall in data.walls:
		wall.draw(canvas)
	if data.gameOver:
		drawGameOver(canvas,data)

##################################################
##Run Function (heavily adapted from socket example)
##################################################
def run(width, height, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def mouse1PressedWrapper(event, canvas, data):
        mouse1Pressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseMotionWrapper(event, canvas, data):
        mouseMotion(event, data)
        redrawAllWrapper(canvas, data)

    def mouse3PressedWrapper(event, canvas, data):
        mouse3Pressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)
    def keyReleasedWrapper(event, canvas, data):
    	keyReleased(event, data)
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
    data.timerDelay = 1 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mouse1PressedWrapper(event, canvas, data))
    canvas.bind("<Motion>", lambda event:
    						mouseMotionWrapper(event, canvas, data))
    root.bind("<Button-3>", lambda event:
                            mouse3PressedWrapper(event, canvas, data))
    root.bind("<KeyPress>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<KeyRelease>", lambda event:
                            keyReleasedWrapper(event, canvas, data))

    timerFiredWrapper(canvas, data)
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(700, 700, serverMsg, server)