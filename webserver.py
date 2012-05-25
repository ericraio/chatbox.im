################################################################
# Imports
################################################################
from flask import (
	Flask,
	request,
	g,
	url_for,
	render_template as render,
	send_from_directory,
	redirect,
	Response
)
import pymongo as mongo
import hashlib
from shared import *

################################################################
# Init
################################################################
app = Flask(__name__)

################################################################
# REMOTE_ADDR
################################################################
class ProxyFix:
	def __init__(self, app):
		self.app = app
	
	def __call__(self, env, start_response):
		if env["REMOTE_ADDR"] == "127.0.0.1":
			realip = env.get("HTTP_X_REAL_IP")
			realhost = env.get("HTTP_X_REAL_HOST")
			if realip:
				env["REMOTE_ADDR"] = realip
			if realhost:
				env["HTTP_HOST"] = realhost
		return self.app(env, start_response)

#install it
app.wsgi_app = ProxyFix(app.wsgi_app)

################################################################
# Before / After
################################################################
@app.before_request
def before_request():
	g.dbconn = mongo.Connection()
	g.db = g.dbconn["chatboxim"]

@app.after_request
def after_request(resp):
	g.dbconn.disconnect()
	return resp

################################################################
# GET
################################################################
@app.route("/", methods = ["GET"])
def index():
	return render("index.html")
	
@app.route("/main", methods = ["GET"])
def main():
	return render("main.html")

@app.route("/register", methods = ["GET"])
def register():
	return render("register.html")
	
@app.route("/home", methods = ["GET"])
def home():
	return render("home.html")

@app.route("/logout", methods = ["GET"])
def logout():
	return "blah blah logged out"

@app.route("/room/<room>", methods = ["GET"])
def chat(room):
	if room == "": room = "main"
	return render("chat.html", env = {"room": room})

@app.route("/img/<name>.jpg", methods = ["GET"])
def image(name):
	return send_from_directory("img", filename = name + ".jpg")

################################################################
# POST
################################################################
@app.route("/register", methods = ["POST"])
def register_post():
	db = g.db.users
	try:
		name = request.form["name"].lower()
		if name == "": return "invalid params"
		email = request.form["email"].lower()
		if email == "": return "email is mandatory"
		pw = request.form["pw"]
		if pw != request.form["cpw"]:
			return "passwords don't match!"
		pwhash = passwordToHash(pw)
	except KeyError:
		return "invalid params"
	if db.find({"name": name}).count() > 0:
		return "name taken!"
	db.insert({
		"name": name,
		"email": email,
		"pwhash": pwhash
	})
	return render("registered.html", name = name)

@app.route("/login", methods = ["POST"])
def login_post():
	db = g.db.users
	name, pwhash = request.form["name"].lower(), passwordToHash(request.form["pw"])
	user = db.find_one({"name": name})
	if not user:
		return "login failure D:"
	if user["pwhash"] != pwhash:
		return "login failure D:"
	sid = generateSessionId()
	db.update({"name": name}, {"$set": {"session": sid}})
	resp = Response(status = 302)
	resp.headers["Location"] = "/main"
	resp.set_cookie("session", sid, max_age = 999999999, httponly = True)
	return resp

################################################################
# Run
################################################################
if __name__ == "__main__":
	app.run(host = "localhost", port = 5000, debug = False)
