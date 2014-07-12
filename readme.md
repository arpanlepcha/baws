# baws: Brandon's Awesome Web Sockets #

I found myself writing lots of Python/JavaScript web applications
involving WebSockets with lots of repetitive code. I tried finding a
way to do this less, but none of the existing libraries worked for me.

I agree with the idea that code should be short. It's the whole point
of not coding in machine language. All of the existing WebSockets
libraries make me write too much code.

`baws` is meant to yield short programs. I'm a fan of the approach
Aaron Swartz used to write web.py: to write the application as if the
ideal library existed, then implement the library to make the
application work. That's what I've tried to do.

## How it works ##

WebSockets let you send plain-text strings back and forth. This isn't
useful enough. No one wants to deal with plain-text strings. The
smartest choice for something that has to be sent between the browser
and server, 99% of the time, seems to be JSON. So that's what `baws`
uses.

The server and browser send the same kind of message to each other:

    {
      "op": "<name ('operation') of the message>",
      ...
    }

Every message is a JSON object with an `op` property specifying the
operation, and whatever other properties you want.

For example, this might happen:

1. Browser sends `{"op": "login", "username": "brandon", "password": "adsfa"}`
2. Server authenticates and sends back `{"op": "logged_in"}`
3. Browser sends `{"op": "get_messages", "count": "4"}`
4. Browser fetches 4 messages and sends back `{"op": "messages", "messages": [...]}`

...and so on.

There are two special operations, `_open` and `_close`, that are
automatically "sent" when the connection is opened and closed.

There is a special kind of message reserved for errors. It takes this
form:

    {"error": "<error message>"}

## Example application ##

Let's look at an example.

### Server-side code ###

    import baws

    app = baws.Application(globals(),
        '_open', 'handle_open', 
        '_close', 'handle_close',
        'login', 'handle_login',
    )


    def handle_open(client, data):
        print 'ip address %s opened connection' % client.request.remote_ip


    def handle_close(client, data):
        print 'ip address %s closed connection' % client.request.remote_ip


    def handle_login(client, data):
        if (data.username, data.password) == ('brandon', 'herpderp'):
            client.send('logged_in')


    if __name__ == '__main__':
        app.run()

### Client-side code ###

    conn = BawsConnection('localhost:6969');

    conn.on('_open', function(data) {
      console.log('Connection opened! Logging in...');
      conn.send('login', {username: 'brandon', password: 'herpderp'});
    });

    conn.on('_close', function(data) {
      console.log('Connection closed...');
    });

    conn.on('logged_in', function(data) {
      console.log('Yay, we\'re logged in!');
    });

One quick thing I want to demonstrate is that `baws` is meant to look
aesthetically pleasing with CoffeeScript. Coffee is already a pretty
language, but lots of frameworks mess things up. Here's what `baws`
looks like:

    conn = BawsConnection 'localhost:6969'

    conn.on '_open', (data) ->
      console.log 'Connection opened! Logging in...'
      conn.send 'login',
        username: 'brandon'
        password: 'herpderp'

    conn.on '_close', (data) ->
      console.log 'Connection closed...'

    conn.on 'logged_in', (data) ->
      console.log 'Yay, we\'re logged in!'

## Documentation ##

The example should IMO be all the documentation necessary. I've
demonstrated all the functions. That's how `baws` works, and you've
seen everything. It's designed to be *simple*.
