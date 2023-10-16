const express = require('express');
const socketio = require('socket.io');
const connectSocket = require('spotify-connect-ws');
const axios = require ('axios');


const app = express();
const server = app.listen(4000);
const io = socketio(server);

io.of('/connect').on('connection', async (socket) => {
  try {
    
    const response = await axios.get('http://localhost:5000/current_access_token');
    const accessToken = response.data.access_token;
    
    if (accessToken) {
      socket.emit('initiate'), { accessToken: accessToken });
    } else {
      console.error('No access token received from the Flask server.');
    }
  } catch (error) {
    console.error('Error fetching the access token from Flask:', error.message);
  }
  socket.on('need_refresh', async () => {
    try {
      const response = await axios.get('http://localhost:5000/refresh_token');
      const refreshedToken = response.data.access_token;
      socket.emit('refreshed_token', { accessToken: refreshedToken });
    } catch (error) {
        console.error('Error refreshing access token:', error.message);
    }
  });
});
