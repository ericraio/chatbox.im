################################################################
# Imports
################################################################
import hashlib
import uuid
import pymongo as mongo

################################################################
# Helpers
################################################################
def passwordToHash(pw): return hashlib.sha256(pw[:3] + pw + pw[5:]).hexdigest()

def _genId():
	return "".join([uuid.uuid4().hex for i in range(2)])

def generateSessionId():
	db = mongo.Connection()["chatboxim"].users
	for i in range(10):
		sid = _genId()
		if not db.find_one({"session": sid}):
			break
	return sid
