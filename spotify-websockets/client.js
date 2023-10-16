const socket = require('socket.io-client')('http://localhost:4000/connect');

socket.on('connect', () => {
    console.log('Connected to server.');
});

socket.on('initial_state', (data) => {
    console.log('Initial state:', data);
});

socket.on('track_change', (track) => {
    console.log('Track Changed:', track);
    
    const trackName = track.name;
    const artistName = artist.name;
    const albumCoverURL = track.album.images[0].url;
    const albumName = trakc.album.name;
});

socket.on('disconnect', () => {
    console.log('Disconnected from the server.');
});
