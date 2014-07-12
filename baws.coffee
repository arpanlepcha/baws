class BawsConnection
  constructor: (server) ->
    @handlers = {}
    @socket = new WebSocket "ws://#{server}/"

    @socket.onmessage = (e) =>
      obj = JSON.parse(e.data)
      console.log obj

      if 'error' of obj
        console.log "ERROR >> #{obj.error}"
        if 'error' of @handlers
          for handler in @handlers['error']
            handler obj

      if 'op' of obj and obj.op of @handlers
        for handler in @handlers[obj.op]
          handler obj

    @socket.onopen = (e) =>
      for handler in @handlers['_open']
        handler {op: '_open'}

  on: (op, cb) ->
    unless @handlers[op]?
      @handlers[op] = []
    @handlers[op].push cb

  send: (op, obj) ->
    obj or= {}
    obj.op = op
    @socket.send(JSON.stringify(obj))

window.BawsConnection = BawsConnection
