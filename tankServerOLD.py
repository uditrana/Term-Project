#Basic Architecture from Rohan's Example for Sockets
import socket
import threading
import random
from queue import Queue

def db(*whatever):
	debug = True
	if debug:
		print(*whatever)

def returnPosition(tankNumber):pass
	# positions = [(50,50,0),(350,50,270),(350,350,180),]


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
	while True:
		msg = serverChannel.get(True, None) #get first item on Q
		db("msg recv: ", msg) #print the message rcvd!
		senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:]) #separates id from msg
		if (msg):
			action = (msg.split(":")[0])
			if action=="forward":
				db ("Player" + str(senderID) + " moved forward!")
				for cID in clientele: #for each client
					if cID != senderID: #if client not the sender
						sendMsg = "forward:"+str(senderID)+":"+"\n" #create message to all other players!
						clientele[cID].send(sendMsg.encode()) #encode and send
			elif action=="backward":
				db ("Player_" + str(senderID) + " moved backward!")
				for cID in clientele: #for each client
					if cID != senderID: #if client not the sender
						sendMsg = "backward:"+str(senderID)+":"+"\n" #create message to all other players!
						clientele[cID].send(sendMsg.encode()) #encode and add it to dict
			elif action=="right":
				db ("Player_" + str(senderID) + " rotated right!")
				for cID in clientele: #for each client
					if cID != senderID: #if client not the sender
						sendMsg = "right:"+str(senderID)+":"+"\n" #create message to all other players!
						clientele[cID].send(sendMsg.encode()) #encode and add it to dict
			elif action=="shoot":
				db ("Player_" + str(senderID) + " shot!")
				for cID in clientele: #for each client
					if cID != senderID: #if client not the sender
						sendMsg = "shoot:"+str(senderID)+":"+"\n" #create message to all other players!
						clientele[cID].send(sendMsg.encode()) #encode and add it to dict
			elif action=="left":
				db ("Player_" + str(senderID) + " rotated left!")
				for cID in clientele: #for each client
					if cID != senderID: #if client not the sender
						sendMsg = "left:"+str(senderID)+":"+"\n" #create message to all other players!
						clientele[cID].send(sendMsg.encode()) #encode and add it to dict
		serverChannel.task_done() #remove item from Q

clientele = {}
currID = 0

serverChannel = Queue(100) #initialize Q
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()
#start_new_thread(serverThread, (clientele, serverChannel))

while True: #loop for adding clients
	client, address = server.accept()
	db(currID) #curr client ID
	for cID in clientele: #tell all other peoples that there is a new player!
		db (repr(cID), repr(currID))
		clientele[cID].send(("newPlayer:%d\n" % currID).encode()) #send new player info!
		client.send(("newPlayer:%d\n" % cID).encode()) #tell the new player about all the old players
	clientele[currID] = client #dont really understand this line
	db("connection received")
	threading.Thread(target = handleClient, args =  #create a new thread for this new client
												(client ,serverChannel, currID, clientele)).start() 
	#start_new_thread(handleClient, (client,serverChannel, currID))
	currID += 1