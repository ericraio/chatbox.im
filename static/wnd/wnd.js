var WND_lastZIndex = 1000;

function Window(title) {
	var self = this;
	self.wnd = document.createElement("div");
	self.titlebar = document.createElement("div");
	self.content = document.createElement("div");
	self.titletext = document.createElement("div");
	self.maxbutton = document.createElement("div");
	self.closebutton = document.createElement("div");
	
	self.wnd.window = self;
	self.titlebar.window = self;
	self.content.window = self;
	self.closebutton.window = self;
	self.maxbutton.window = self;
	self.titletext.window = self;
	
	self.titlebar.appendChild(self.titletext);
	self.titlebar.appendChild(self.closebutton);
	self.titlebar.appendChild(self.maxbutton);
	self.wnd.appendChild(self.titlebar);
	self.wnd.appendChild(self.content);
	
	self.titletext.innerHTML = title;
	self.maxbutton.innerHTML = "O";
	self.closebutton.innerHTML = "X";
	
	self.movable = true;
	
	self.dragged = false;
	self.dragStartX = 0;
	self.dragStartY = 0;
	self.dragStartLeft = 0;
	self.dragStartTop = 0;
	
	self.maximized = false;
	self.pX = 0;
	self.pY = 0;
	self.pW = 0;
	self.pH = 0;
	self.pMV = false;
	
	self.wnd.style.position = "absolute";
	self.wnd.style.left = "0px";
	self.wnd.style.top = "0px";
	self.wnd.style.zIndex = WND_lastZIndex++;
	self.wnd.style.overflow = "hidden";
	
	self.titlebar.style.overflow = "hidden";
	
	self.content.style.overflow = "hidden";
	
	self.closebutton.style.cssFloat = "right";
	self.closebutton.style.cursor = "pointer";
	
	self.maxbutton.style.cssFloat = "right";
	self.maxbutton.style.cursor = "pointer";
	
	self.titletext.style.cssFloat = "left";
	
	self.wnd.addClassName("wnd_full");
	self.titlebar.addClassName("wnd_titlebar");
	self.content.addClassName("wnd_content");
	
	self.close = function() {
		self.wnd.parentNode.removeChild(self.wnd);
	};
	
	self.setPosition = function(x, y) {
		self.wnd.style.left = x;
		self.wnd.style.top = y;
	};
	
	self.getPositionX = function() {
		return self.wnd.style.left;
	};
	self.getPositionY = function() {
		return self.wnd.style.top;
	};
	
	self.hide = function() {
		self.wnd.style.display = "none";
	};
	self.show = function() {
		self.wnd.style.display = "block";
	};
	
	self.maximize = function() {
		if(self.maximized) {return;}
		self.wnd.style.position = "fixed";
		self.pX = self.wnd.style.left;
		self.pY = self.wnd.style.top;
		self.pW = self.wnd.style.width;
		self.pH = self.wnd.style.height;
		self.pMV = self.movable;
		self.wnd.style.left = "0px";
		self.wnd.style.top = "0px";
		self.wnd.style.width = "100%";
		self.wnd.style.height = "100%";
		self.movable = false;
		self.maximized = true;
	};
	
	self.minimize = function() {
		if(!self.maximized) {return;}
		self.wnd.style.position = "absolute";
		self.wnd.style.left = self.pX;
		self.wnd.style.top = self.pY;
		self.wnd.style.width = self.pW;
		self.wnd.style.height = self.pH;
		self.movable = self.pMV;
		self.maximized = false;
	};
	
	self.toggleMaximized = function() {
		if(self.maximized) {self.minimize();}
		else {self.maximize();}
	}
	
	self.dragStart = function(e) {
		if(!self.movable) {return;}
		self.dragged = true;
		self.dragStartX = e.clientX + window.scrollX;
		self.dragStartY = e.clientY + window.scrollY;
		self.dragStartLeft = parseInt(self.wnd.style.left, 10);
		self.dragStartTop = parseInt(self.wnd.style.top, 10);
		self.wnd.style.zIndex = WND_lastZIndex++;
		document.addEventListener("mousemove", self.dragStep, true);
		document.addEventListener("mouseup", self.dragStop, true);
		e.preventDefault();
	};
	self.dragStep = function(e) {
		var diffX = self.dragStartX - (e.clientX + window.scrollX);
		var diffY = self.dragStartY - (e.clientY + window.scrollY);
		self.wnd.style.left = (self.dragStartLeft - diffX) + "px";
		self.wnd.style.top = (self.dragStartTop - diffY) + "px";
		e.preventDefault();
	};
	self.dragStop = function(e) {
		self.dragged = false;
		document.removeEventListener("mousemove", self.dragStep, true);
		document.removeEventListener("mouseup", self.dragStop, true);
		e.preventDefault();
	};
	
	self.titlebar.addEventListener("mousedown", self.dragStart, true);
	self.closebutton.addEventListener("mouseup", self.close, true);
	self.maxbutton.addEventListener("mouseup", self.toggleMaximized, true);
}
