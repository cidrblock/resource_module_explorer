function ConvertFormToJSON(form){
    var array = jQuery(form).serializeArray();
    var json = {};
    jQuery.each(array, function() {
        if (this.name in json) {
          if (!$.isArray(json[this.name])) {
            json[this.name] = [json[this.name]]
          }
          json[this.name].push(this.value)
        } else {
          json[this.name] = this.value || '';
        }
    });
    return json;
}
function connect() {
  log("Attempting websocket connection.")
  var ansi_up = new AnsiUp;
  var ws = (window.location.protocol=='https:'&&'wss://'||'ws://')+window.location.host+'/ws';
  conn = new WebSocket(ws);
  conn.onopen = function() {
    log("Connected via websocket.")
  };
  conn.onmessage = function(msg) {
    var html = ansi_up.ansi_to_html(JSON.parse(msg.data).event.stdout);
    log(html)
  };

  conn.onclose = function(e) {
    msg = 'Socket is closed. Reconnect will be attempted in 1 second.' + e.reason;
    log(msg)
    setTimeout(function() {connect();}, 1000);
  };

  ws.onerror = function(err) {
    msg = 'Socket encountered error:', err.message, 'Closing socket';
    log(msg)
    ws.close();
  };
}
function log(msg) {
  var console_pre = document.getElementById('console')
  var console_div = document.getElementById('dconsole')
  console_pre.innerHTML += msg + '<br>';
  dconsole.scrollTop = dconsole.scrollHeight
}

// limit the contents of the editor to the form resources
function gatherResources(editor, resources) {
  config = {}
  if (resources.includes('all')) {
    config = editor
  } else {
    for (key in editor) {
      if (resources.includes(key)) {
        config[key] = editor[key]
      }
    }
  }
  return config
}

document.addEventListener('DOMContentLoaded', function() {
  // make the websocket connection
  connect();

  // retrieve the os list
  var request = new XMLHttpRequest();
  request.open('GET', '/oss');
  request.setRequestHeader('Content-Type', 'application/json');
  request.onload = function() {
      if (request.status === 200) {
          data = JSON.parse(request.responseText);
          var input = document.getElementById("os");
          for(var i = 0; i < data.length; i++) {
              var item = data[i];
              var opt = document.createElement('option');
              opt.text = item;
              opt.value = item;
              input.add(opt)
          }
          log("Retrieved OS list.")
      }
  };
  request.send();

  // update the resource list when the OS changes
  document.getElementById("os").addEventListener('input', function (evt) {
    var os = this.value;
    var request = new XMLHttpRequest();
    request.open('POST', '/resources');
    request.setRequestHeader('Content-Type', 'application/json');
    request.onload = function() {
        if (request.status === 200) {
            data = JSON.parse(request.responseText);
            var input = document.getElementById("resources");
            for(var i = 0; i < data.length; i++) {
                var item = data[i];
                var opt = document.createElement('option');
                opt.text = item;
                opt.value = item;
                input.add(opt)
            }
            $('.resources').val('default').selectpicker('refresh');
            log("Retrieved resource list for " + os + '.')
        }
    };
    request.send(JSON.stringify({"os": os}));
  });

  // enable the become password input when enable checked
  document.getElementById('become').onchange = function() {
      document.getElementById('become_password').disabled = !this.checked;
  };

  // define the ditor for use
  const options = {"modes": ['view', 'form', 'tree', 'code', 'text', 'preview']}
  const editor = new JSONEditor(document.getElementById("jsoneditor"), options)

  // handle the playbook preview post
  document.getElementById('preview_playbook').addEventListener("click", function() {
    var form = document.getElementById('form')
    if(form.checkValidity()) {
      var request = new XMLHttpRequest();
      var json = ConvertFormToJSON(document.getElementById('form'));
      if (json.playbook_name == "ucrm") {
        json.config = gatherResources(editor.get(), json.resources)
      }
      request.open('POST', '/render_playbook');
      request.setRequestHeader('Content-Type', 'application/json');
      request.onload = function() {
          if (request.status === 200) {
              data = JSON.parse(request.responseText);
              document.getElementById('playbook_text').innerHTML = data.playbook
              hljs.highlightBlock(document.getElementById('playbook_text'))
              $('#playbook_modal').modal('show');
          }
      };
      request.send(JSON.stringify(json));
    } else {
      form.reportValidity();
    }
  });

  // handle the inventory post
  document.getElementById('preview_inventory').addEventListener("click", function() {
    var form = document.getElementById('form')
    if(form.checkValidity()) {
      var request = new XMLHttpRequest();
      var json = ConvertFormToJSON(document.getElementById('form'));
      request.open('POST', '/render_inventory');
      request.setRequestHeader('Content-Type', 'application/json');
      request.onload = function() {
        if (request.status === 200) {
            data = JSON.parse(request.responseText);
            field = document.getElementById('inventory_text')
            field.innerHTML = data.inventory
            hljs.highlightBlock(field)
            $('#inventory_modal').modal('show');
        }
      };
      request.send(JSON.stringify(json));
    } else {
      form.reportValidity();
    }
  });

  // handle the playbook run
  document.getElementById('run').addEventListener("click", function() {
    var form = document.getElementById('form')
    if(form.checkValidity()) {
      $('#playbook_modal').modal('hide');
      $('#spin').modal('show');
      document.getElementById('console').innerHTML = '';
      var request = new XMLHttpRequest();
      var json = ConvertFormToJSON(document.getElementById('form'));
      if (json.playbook_name == "ucrm") {
        json.config = gatherResources(editor.get(), json.resources)
      }
      request.open('POST', '/run_playbook');
      request.setRequestHeader('Content-Type', 'application/json');
      request.onload = function() {
        if (request.status === 200) {
            data = JSON.parse(request.responseText);
            $('#spin').modal('hide');
            editor.set(data);
        }
      };
      request.send(JSON.stringify(json));
    } else {
      form.reportValidity();
    }
  });
});
