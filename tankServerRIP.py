#Basic Architecture from Rohan's Example for Sockets
#Almost every method has been heavily altered except for handleClient
import socket
import threading
import random
from queue import Queue

def db(*whatever):
	debug = True
	if debug:
		print(*whatever)

def position(tankNumber):
	positions = [(50,50,0),(750,750,180),(750,50,270),(50,750,90)]
	return positions[tankNumber]

spawns = []

HOST = "128.237.162.243" 
PORT = 50003
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
db("looking for connection")

def handleClient(client, serverChannel, cID, clientele): #this adds the client ID and msg to Q
	client.setblocking(1)
	msg = ""
	while True:
		try:
			msg += client.recv(10).decode("UTF-8") #creates message based on input
			command = msg.split("\n") #splits message based on \n
			while (len(command) > 1): #if we have a complete command
				readyMsg = command[0] #the first part is rdy message to be run
				msg = "\n".join(command[1:]) #the rest is shit that begins the next msg
				serverChannel.put(str(cID) + "_" + readyMsg) #add client ID and rdy msg to Q
				command = msg.split("\n") #go to next command (if there is one)
		except: #if gets bad shit, remove client
			clientele.pop(cID)
			return

def serverThread(clientele, serverChannel): #processes shit on the Q
	peopleReady = 0
	while True:
		msg = serverChannel.get(True, None) #get first item on Q
		db("msg recv: ", msg) #print the message rcvd!
		senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:]) #separates id from msg
		if (msg):
			action = (msg.split(":")[0])
			if action=="keyPressed":
				dir = (msg.split(":")[1])
				sendMsg  = action+":"+dir+":"+str(senderID)+":\n"#msg for all players
				for cID in clientele: #for each client
					if cID != senderID: #if client not the sender
						clientele[cID].send(sendMsg.encode()) #encode and send to Client object in dict
			if action=="keyReleased":
				dir = (msg.split(":")[1])
				sendMsg  = action+":"+dir+":"+str(senderID)+":\n"#msg for all players
				for cID in clientele: 
					if cID != senderID:
						clientele[cID].send(sendMsg.encode())
				# if dir=="forward":
				# 	db ("Player" + str(senderID) + " pressed forward!")
				# 	for cID in clientele: #for each client
				# 		if cID != senderID: #if client not the sender
				# 			sendMsg = "keyPressed:forward:"+str(senderID)+":"+"\n" #create message to all other players!
				# 			clientele[cID].send(sendMsg.encode()) #encode and send to Client object in dict
				# elif dir=="backward":
				# 	db ("Player_" + str(senderID) + " pressed backward!")
				# 	for cID in clientele: 
				# 		if cID != senderID: 
				# 			sendMsg = "keyPressed:backward:"+str(senderID)+":"+"\n" 
				# 			clientele[cID].send(sendMsg.encode()) 
				# elif dir=="right":
				# 	db ("Player_" + str(senderID) + " pressed right!")
				# 	for cID in clientele:
				# 		if cID != senderID:
				# 			sendMsg = "keyPressed:right:"+str(senderID)+":"+"\n"
				# 			clientele[cID].send(sendMsg.encode())
				# elif dir=="left":
				# 	db ("Player_" + str(senderID) + " pressed left!")
				# 	for cID in clientele:
				# 		if cID != senderID: 
				# 			sendMsg = "keyPressed:left:"+str(senderID)+":"+"\n"
				# 			clientele[cID].send(sendMsg.encode())
			elif action=="shoot":
				db ("Player_" + str(senderID) + " shot!")
				for cID in clientele: 
					if cID != senderID:
						sendMsg = "shoot:"+str(senderID)+":"+"\n" 
						clientele[cID].send(sendMsg.encode())
			elif action=="vertWall":
				db ("Player_" + str(senderID) + " added a vertWall")
				print (msg)
				msg += "\n" #dont forget the goddamn new line char
				for cID in clientele:
					if cID != senderID:
						clientele[cID].send(msg.encode()) #just send exact same message
			elif action=="horWall":
				db ("Player_" + str(senderID) + " added a horWall")
				msg += "\n"
				for cID in clientele:
					if cID != senderID:
						clientele[cID].send(msg.encode())
			elif action=="spawn":
				db ("Player_" + str(senderID) + " added a spawn")
				msg += "\n"
				for cID in clientele:
					if cID != senderID:
						clientele[cID].send(msg.encode())
				msg = msg.split(":")
				pos = (int(msg[1]),int(msg[2]),int(msg[3]))
				spawns.append(pos)
			elif action=="removeWall":
				msg += "\n"
				for cID in clientele:
					if cID != senderID:
						clientele[cID].send(msg.encode())
			elif action=="removeSpawn":
				msg += "\n"
				for cID in clientele:
					if cID != senderID:
						clientele[cID].send(msg.encode())
				msg = msg.split(":")
				x,y = int(msg[1]),int(msg[2])
				for spawn in spawns:
					if spawn[0] == x and spawn[1] == y:
						spawns.remove(spawn)
						break
			elif action=="ready":
				peopleReady += 1
				print ("peopleReady:", peopleReady)
				if peopleReady == len(clientele):
					sendStart()
			elif action=="unready":
				peopleReady -= 1
				print ("peopleReady:", peopleReady)
			elif action=="cursor":
				msg += "\n"
				for cID in clientele:
					if cID != senderID:
						clientele[cID].send(msg.encode())
		serverChannel.task_done()
def sendStart():
	# for cID in clientele:
	# 	for number in range(len(spawns)):
	# 		if number==cID:
	# 			x,y,ang = spawns[number]
	# 			clientele[cID].send(("player:%d:%d:%d:%d\n" %(cID,x,y,ang)).encode())
	# 		else:
	# 			x,y,ang = spawns[number]
	# 			clientele[cID].send(("newPlayer:%d:%d:%d:%d\n" %(cID,x,y,ang)).encode())
	msg = "start:\n"
	for cID in clientele:
		clientele[cID].send(msg.encode())

clientele = {}
currID = 0

serverChannel = Queue(100) #initialize Q
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()
#start_new_thread(serverThread, (clientele, serverChannel))

while True: #loop for adding clients
	client, address = server.accept()
	# db(currID) #curr client ID
	x,y,ang = position(currID) #get the position of new tank
	print(x)
	print (y)
	print (ang)
	client.send(("player:%d:%d:%d:%d\n" %(currID,x,y,ang)).encode()) #send player info!
	for cID in clientele: #tell all other peoples that there is a new player!
		db (repr(cID), repr(currID))
		clientele[cID].send(("newPlayer:%d:%d:%d:%d\n" %(currID,x,y,ang)).encode()) #send new player info!
		x,y,ang = position(cID) #get the position of other tanks
		client.send(("newPlayer:%d:%d:%d:%d\n" %(cID,x,y,ang)).encode()) #tell the new player about all the old players
	clientele[currID] = client #adds a client object to dict?
	db("connection received")
	threading.Thread(target = handleClient, args =  #create a new thread for this new client
												(client ,serverChannel, currID, clientele)).start()
	currID += 1