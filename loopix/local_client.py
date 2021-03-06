from client import Client
import format3
import petlib
import os
import sys
from twisted.internet import reactor
from twisted.protocols import basic
from twisted.internet import stdio
import time
import supportFunctions as sf
import random
from twisted.python import usage
from twisted.application import service, internet
from twisted.python import usage
from twisted.plugin import IPlugin

class ClientEcho(basic.LineReceiver):
	from os import linesep as delimiter
	def __init__(self, client):
		self.client = client
		reactor.listenUDP(port, self.client)

	def connectionMade(self):
		self.transport.write('>>> ')

	def lineReceived(self, line):
		if line.upper() == "-P":
			print "Hello world"
		elif line.upper() == "-T":
			try:
				self.client.sendTagedMessage()
			except Exception, e :
				print str(e)
		elif line.upper() == "-E":
			reactor.stop()
		elif line.upper() == "-M":
			try:
				friends = random.sample(self.client.usersPubs, 3)
				print "Friends group: ", friends
				recipient = random.choice(friends)
			except Exception, e:
				print str(e)
			print recipient.provider.name
			#self.targetSending(friends)
			self.targetSending(recipient)
		else:
			print "Command not found"
		self.transport.write('>>> ')

	def targetSending(self, recipient):
		#recipient = random.choice(group)
		print ">> SENDING TO SELECTED CLIENT ", recipient
		try:
			path = self.client.takePathSequence(self.client.mixnet, self.client.PATH_LENGTH)
			msgF = "RANDOMTARGET" + sf.generateRandomNoise(1000)
			msgB = "RANDOMTARGET" + sf.generateRandomNoise(1000)
			self.client.sendMessage(recipient, path, msgF, msgB)
			reactor.callLater(10, self.targetSending, recipient)
		except Exception, e:
			print str(e)

class Options(usage.Options):
	optParameters = [["test", "t", False, "The client test mode"]]

if __name__ == "__main__":

	if not (os.path.exists('secretClient.prv') and os.path.exists("publicClient.bin")):
		raise Exception("Key parameter files not found")

	options = Options()
	setup = format3.setup()
	G, o, g, o_bytes = setup

	secret = petlib.pack.decode(file("secretClient.prv", "rb").read())

	try:
		data = file("publicClient.bin", "rb").read()
		_, name, port, host, _, prvname = petlib.pack.decode(data)
		
		if "--test" in sys.argv:
			client = Client(setup, name, port, host, privk = secret, providerId=prvname, testUser=True)
		else:
			client = Client(setup, name, port, host, privk = secret, providerId=prvname, testUser=False)

		if "--mock" not in sys.argv:
			stdio.StandardIO(ClientEcho(client))
			reactor.run()

	except Exception, e:
		print str(e)

else:
	setup = format3.setup()
	G, o, g, o_bytes = setup

	secret = petlib.pack.decode(file("secretClient.prv", "rb").read())

	data = file("publicClient.bin", "rb").read()
	_, name, port, host, _, prvname = petlib.pack.decode(data)


	client = Client(setup, name, port, host, privk = secret, providerId=prvname)

	udp_server = internet.UDPServer(port, client)
	application = service.Application("Client")
	udp_server.setServiceParent(application)

	# except Exception, e :
	# 	print str(e)
