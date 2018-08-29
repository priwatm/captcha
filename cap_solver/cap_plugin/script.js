const URL          = 'wss://localhost/capsolver/socket';
const DEBUG        = 'true';
const WINDOW_POPUP = 'popup';
const WINDOW_MWIND = 'mwind';
if (chrome.tabs) { var WINDOW = WINDOW_POPUP;}
else 			 { var WINDOW = WINDOW_MWIND;}


(function(exports) {

  var $ = document.querySelectorAll.bind(document);

  exports.pureTabs = {

    toggle: function(e) {
      var activeClassName = this.activeClassName,
          oldSection = $('[data-puretabs]')[0],
          newSection = $(e.currentTarget.hash)[0];

      removeClass($(activeClassName)[0], activeClassName.substr(1));
      addClass(e.currentTarget, activeClassName.substr(1));

      oldSection.style.display = 'none';
      oldSection.removeAttribute('data-puretabs');

      newSection.style.display = 'block';
      newSection.setAttribute('data-puretabs', '');
    },

    init: function(className, activeClassName) {
      var self = this;

      self.className = '.' + className || '.puretabs';
      self.activeClassName = '.' + activeClassName || '.puretabs--active';

      var links = [].slice.call($(self.className));

      links.forEach(function(link) {

        if (!containsClass(link, self.activeClassName.substr(1))) {
          $(link.hash)[0].style.display = 'none';
        } else {
          $(link.hash)[0].setAttribute('data-puretabs', '');
        }

        link.addEventListener('click', function(e) {
          e.preventDefault();
          self.toggle.call(self, e)
        });

      });
    }

  };


  //  Helpers
  function addClass(e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", "g");
    if (re.test(e.className)) return;
    e.className = (e.className + " " + c).replace(/\s+/g, " ").replace(/(^ | $)/g, "")
  }

  function removeClass(e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", "g");
    e.className = e.className.replace(re, "$1").replace(/\s+/g, " ").replace(/(^ | $)/g, "");
  }

  function containsClass(e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", "g");
    return re.test(e.className) ? true : false;
  }

})(window);

pureTabs.init('tabs__link', 'tabs__link--active');

			
class Message {
	constructor(socket=null) {
		this.source  = null;
		this.url     = null;
		this.type    = null;
		this.action  = null;
		this.params  = {};
		this.results = [];
		this.socket  = socket;
	}
	from_str(s) {
		if(!s) return;
		s = JSON.parse(s);
		this.source  = s.source;
		this.url     = s.url;
		this.type    = s.type;
		this.action  = s.action;
		this.params  = s.params;
		this.results = s.results;
		return this
	}
	to_json() {
		this.source = WINDOW;
		this.url    = window.location.href;
		if (this.type != 'command') this.action = null;
		if (this.type != 'results') this.results = [];
		if (this.type == 'results') this.params = null;
		return JSON.stringify(this)
	}
	act(obj) {
		if(this.type == 'command' && this.action) {
			let func = obj[this.action];
			if (func) {
				out('Action "' + this.action + '" will be performed.');
				func(obj, this); return true
			}
		}
		error('Unknown command: '+this.action+'.', 'act', 'Message');
		return false
	}
	send(socket=null) {
		if (socket) {
			this.socket = socket;
		}
		if (!this.socket) {
			out('ERROR: Connection with server is broken.');
			return
		}
		let self = this;
		socket.waitForConnection(function() { self.socket.write(self.to_json()); });
	}
}

class Manager {
	constructor() {
		this.socket = null;
		this.timer = null;
	}
	connected(socket) {
		this.socket = socket;
	}
	disconnected() {
		this.socket = null;
	}
	interaction(s) {
		let MS = new Message(this.socket).from_str(s);
		MS.act(this);
	}
	start(self, MS) {
		let img = document.querySelector('[class="captcha-img"]');
		MS.type = 'command';
		MS.action = 'solve_captcha';
		if (img && img.src) {
			MS.params = {'captcha_url': img.src};
			MS.send(socket);
		}		
	}
	write_solution(self, MS) {
		let field_cap_txt = document.querySelector('#code-input');
		field_cap_txt.value = MS.params['captcha_text'];
	}
}

function create_socket(manager) {
	let socket = new WebSocket(URL);

	socket.onopen = function(event) {
		out('WebSocket is opened.');
		manager.connected(socket);
	};
	socket.onmessage = function(event) {
		out('WebSocket recieved a message: ', event.data);
		manager.interaction(event.data);
	};
	socket.onclose = function(event) {
		out('WebSocket is closed.');
		manager.disconnected();
	};
	socket.onerror = function(event) {
		out("WebSocket is closed with error.");
		manager.disconnected();
	};
	socket.write = function(out_message) {
		if(!out_message) {return};
		out('WebSocket is going to send: ', out_message);
		socket.send(out_message);
	};
	socket.waitForConnection = function (callback, interval=10) {
	    if (socket.readyState === 1) {
	        callback();
	    } else {
	        var that = this;
	        setTimeout(function () {
	            that.waitForConnection(callback, interval);
	        }, interval);
	    }
	}
	return socket;
}

function addZero(i) {
	if (i < 10) {
		return '0' + i;
	}
	return i;
}

function formatDate(date) {
	var hour = addZero(date.getHours());
	var mins = addZero(date.getMinutes());
	var secs = addZero(date.getSeconds());
	var y = date.getFullYear();
	var m = addZero(date.getMonth()+1);
	var d = addZero(date.getDate())
	return y + '-' + m + '-' + d + ' ' + hour + ':' + mins + ':' + secs;
}

function out(txt, obj=null) {
	if (!DEBUG) {
		return;
	}
	var txt_d = formatDate(new Date());
	var txt_o = '';
	if (obj != null) {
		txt_o = '\n  ' + JSON.stringify(obj); //.replace(/\"/g, ""); 
	}
	if (WINDOW == WINDOW_POPUP) {
		var res = '\n' + txt_d + ' | (POPUP) : \n  ' + txt + txt_o;
		chrome.tabs.executeScript({code: 'console.log(`'+res+'`)'});
	}
	if (WINDOW == WINDOW_MWIND) {
		var res = '\n' + txt_d + ' | (MWIND) : \n  ' + txt + txt_o;
    	console.log(res);
    }
}

function error(text, func, cl) {
	out('Error (in '+cl+'.'+func+'): '+text);
	MS = new Message(socket)
	MS.type = 'error'
	MS.params = {'error': {'cl': cl, 'func': func, 'text': text}};
	MS.send();
}

let manager = new Manager();
let socket = create_socket(manager);

if (WINDOW == WINDOW_POPUP) {
	let MS = new Message(socket);
	MS.type = 'command';
	MS.action = 'get_info';
	MS.send(socket);
}
if (WINDOW == WINDOW_MWIND) {
	let MS = new Message(socket);
	manager.start(manager, MS);
}