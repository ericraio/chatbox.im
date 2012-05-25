var webio = {
	Session: function(node) {
		var self = this;
		self.node = node;
		self.open = false;
		self.session = null;
		
		self.start = function(msg) {
			if(self.open) {throw "trying to open an already open session";}
			new Ajax.Request(node + "/start", {
				method: "post",
				parameters: $H({init: msg}),
				onSuccess: function(resp) {
					var msg = webio.parseMessage(resp.responseText);
					if(msg.type == 3) { //woah, somehow our request got denied
						self.onDenied(msg.data);
						return;
					}
					self.open = true;
					self.session = msg.data;
					self.onAccepted();
					self._poll();
				},
				onFailure: function(resp) {
					self.onConnectFail();
				}
			});
		};
		self.send = function(msg) {
			if(!self.open) {throw "trying to send a message on a closed session";}
			new Ajax.Request(node + "/msg", {
				method: "post",
				parameters: $H({session: self.session, msg: msg}),
				onSuccess: function() {}
			});
		}
		self.close = function() {
			if(!self.open) {throw "trying to close an already closed session";}
			new Ajax.Request(node + "/end", {
				method: "post",
				parameters: $H({session: self.session}),
				onSuccess: function() {}
			});
			self.open = false;
			self.onDisconnect();
		};
		
		self._poll = function() {
			if(!self.open) {return;}
			setTimeout(function() {
				new Ajax.Request(node + "/poll", {
					method: "post",
					parameters: $H({session: self.session}),
					onSuccess: function(resp) {
						var msgs = webio.unpackMessages(resp.responseText);
						msgs.each(function(m) {
							var msg = webio.parseMessage(m);
							if(msg.type == 3) { //disconnected
								if(self.open) {
									self.open = false;
									self.onDisconnect();
								}
								return;
							}
							else if(msg.type == 4) { //overenthousiastic polling
								return;
							}
							else if(msg.type == 2) { //woot message
								self.onMessage(msg.data);
							}
							self._poll(); //they see me pollin', they hatin', they trollin'
						});
					},
					onFailure: function(resp) {
						if(self.open) {
							self.open = false;
							self.onDisconnect();
						}
						return;
					}
				});
			}, 0);
		};
		
		self.onAccepted = function() {};
		self.onDenied = function(reason) {};
		self.onConnectFail = function() {};
		self.onMessage = function(msg) {};
		self.onDisconnect = function() {};
	},
	
	packMessages: function(msgs) {
		return msgs.join("\0");
	},
	unpackMessages: function(msgs) {
		return msgs.split("\0");
	},
	makeMessage: function(type, msg) {
		return type + ":" + msg;
	},
	parseMessage: function(msg) {
		var data = msg.split(":");
		return {type: parseInt(data[0]), data: data.slice(1).join(":")};
	}
};
