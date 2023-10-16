import express from 'express';
import socketio from 'socket.io';
from axios from 'axios';
import connectSocket from 'spotify-connect-ws';

const app = express();
const expressServer = app.listen(4001);

const io = socketio(expressServer);
io.of('connect').on('connection', connectSocket);

const bunServer = Bun.serve({
  port: 4000,
  fetch(req, server) {
      const url = new URL(req.url);

      if (url.pathname === '/current_access_token' || url.pathname === '/refresh_token') {
        return axios.get('http://localhost:5000${url.pathname}')
            .then(response => { 
              return new Response(JSON.stringify(response.data), { status: 200, headers: { 'Content-Type': 'application/json' }});
        })
        .catch(error => {
            console.error('Error fetching from Flask at ${url.pathname}:', error.message);
            return new Response("Internal Server Error", { status: 500});
        });
    } else {
        return new Response("Not Found", { status: 404 });
    }
  }
});

console.log('Bun server running on port 4000');
console.log('Express Server is running on port 4001');
