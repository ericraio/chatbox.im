Chatbox.im
==========

Description
-----------

Chat

How to Install
----------------

+ Install nginx and python on the server
+ Install the python modules flask, pymongo, txmongo and twisted (you can use `sudo pip install` or `sudo easy_install` to do so)
+ Install webio from https://github.com/lumirayz/webio (basically clone the repo and run setup.py as root)
+ Grab a kitten and hug it while you wait for it to install
+ Edit the nginx.conf to work with the server (should be pretty straightforward)
+ Start nginx
+ Start the chatserver with `python chatserver.py` (assuming python links to python 2)
+ Start the webserver with `python webserver.py` (again, assuming python links to python 2)
+ I guess that should be all, might've missed something
