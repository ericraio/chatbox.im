################################################################
# Imports
################################################################

####
# Twisted
####
from twisted.web import resource, server
from twisted.internet import defer
from twisted.python import failure
from twisted.python.util import mergeFunctionMetadata
import webio
import txmongo

####
# Std
####
import json
import random
import uuid

####
# Shared
####
from shared import *

################################################################
# Helpers
################################################################
def c(_tp, **params): return json.dumps(dict({"type": _tp}, **params)) #c, because it looks like a cup of coffee

################################################################
# Room
################################################################
class Room:
	def __init__(self, name, mods = []):
		self.name = name
		self.mods = mods
		self.sessions = list()
	
	def add(self, session):
		self.sessions.append(session)
	
	def remove(self, session):
		self.sessions.remove(session)
	
	def broadcast(self, msg):
		for session in self.sessions:
			session.send(msg)

rooms = dict()
rooms["main"] = Room("main", mods = ["lumi", "atrosity", "pup"])

################################################################
# Instance ID
################################################################
iids = dict()

################################################################
# Inherit WebIOResource
################################################################
class Chat(webio.WebIOResource):
	def onConnect(self, session, init):
		init = init.lower()
		if init not in rooms:
			print session.sid, "denied"
			return webio.Denied("Invalid room!")
		session["room"] = init
		session["name"] = "visitor" + str(random.randint(100, 999))
		session["anon"] = True
		session["iid"] = uuid.uuid4().hex
		iids[session["iid"]] = session
		room = rooms[session["room"]]
		room.broadcast(c("join", src = session["name"]))
		room.add(session)
		room.broadcast(c("usrl", cmd = "count", amt = len(room.sessions)))
		session.send(c("usrl", cmd = "init", users = [{"iid": s["iid"], "src": s["name"]} for s in filter(lambda x: not x["anon"], room.sessions)]))
		print session["name"], "connected"
	
	def onDisconnect(self, session):
		room = rooms[session["room"]]
		room.remove(session)
		del iids[session["iid"]]
		room.broadcast(c("usrl", cmd = "count", amt = len(room.sessions)))
		if not session["anon"]:
			room.broadcast(c("usrl", cmd = "remove", iid = session["iid"]))
		print session["name"], "disconnected"
	
	def onMessage(self, session, msg):
		room = rooms[session["room"]]
		try:
			data = json.loads(msg)
			if "type" not in data: return
			f = "cmd_" + data["type"]
			if hasattr(self, f):
				getattr(self, f)(room, session, data)
		except ValueError:
			pass
	
	def cmd_msg(self, room, session, data):
		if "msg" not in data: return
		room.broadcast(c("msg", src = session["name"], msg = data["msg"], admin = session["admin"], anon = session["anon"]))
	
	def cmd_slc(self, room, session, data):
		if "cmd" not in data: return
		if "args" not in data: data["args"] = None
		f = "slc_" + data["cmd"]
		if hasattr(self, f):
			getattr(self, f)(room, session, data["args"])
	
	def slc_nick(self, room, session, args):
		name = args.lower()
		if not name.isalnum():
			session.send(c("error", msg = "names must be alphanumeric"))
			return
		if not session["anon"]:
			room.broadcast(c("usrl", cmd = "remove", iid = session["iid"]))
		session["admin"] = False
		session["name"] = name
		session["anon"] = True
	
	@defer.inlineCallbacks
	def slc_login(self, room, session, args):
		data = args.split(" ", 1)
		name = data[0].lower()
		if not name.isalnum():
			session.send(c("error", msg = "names must be alphanumeric"))
		if len(data) > 1: pw = data[1]
		else:
			session.send(c("error", msg = "no password"))
			return
		conn = yield txmongo.MongoConnection()
		user = yield conn["chatboxim"].users.find_one({"name": name})
		if user and passwordToHash(pw) == user["pwhash"]:
			if not session["anon"]:
				room.broadcast(c("usrl", cmd = "remove", iid = session["iid"]))
			session["anon"] = False
			session["name"] = name
			session["admin"] = session["name"] in room.mods
			room.broadcast(c("usrl", cmd = "add", src = session["name"], iid = session["iid"]))
			return
		session.send(c("error", msg = "invalid password or user doesn't exist"))
	
	def slc_me(self, room, session, args):
		if args == None: return c("error", msg = "nothing to emote")
		room.broadcast(c("emote", src = session["name"], msg = args, admin = session["admin"], anon = session["anon"]))
	
	def slc_w(self, room, session, args): return self.slc_whis(room, session, args) #alias
	def slc_whis(self, room, session, args):
		if session["anon"]:
			session.send(c("error", msg = "visitors can't whisper"))
			return
		data = args.split(" ", 1)
		tg = data[0]
		if len(data) > 1: msg = data[1]
		else:
			session.send(c("error", msg = "no message to whisper"))
			return
		found = False
		for sess in room.sessions:
			if not sess["anon"] and sess["name"] == tg:
				sess.send(c("whis", src = session["name"], msg = msg))
				found = True
		if found:
			session.send(c("sent", src = session["name"], tg = tg, msg = msg))
			return
		else:
			session.send(c("error", msg = "user not found"))
			return
	
	def slc_kick(self, room, session, args):
		if not session["admin"]: return
		args = args.lower()
		for sess in room.sessions:
			if sess["name"].lower() == args:
				sess.close()
		room.broadcast(c("kick", src = session["name"], tg = args))
	
	def slc_reload(self, room, session, args):
		if not session["admin"]:
			session.send(c("error", msg = "only admins can refresh"))
			return
		room.broadcast(c("refresh"))
	
	def slc_isadmin(self, room, session, args):
		if session["admin"]: m = "Yes"
		else: m = "No"
		session.send(c("error", msg = m))

################################################################
# Run
################################################################
if __name__ == "__main__":
	from twisted.internet import reactor
	reactor.listenTCP(8080, server.Site(Chat()), interface = "localhost")
	reactor.run()
