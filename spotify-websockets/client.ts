import openSocket from 'socket.io-client';

async function fetchAccessToken() {
  try {
    const response = await fetch('http://localhost:4000/get_access_token');
    if (response.ok) {
      const data = await response.json();
      return data.access_token;
    } else {
      throw new Error('Failed to fetch access token');
    }
  } catch (error) {
    console.error('Error fetching access token:', error);
    return null;
  }
}

async function initiateSocketConnection() {
  const accessToken = await fetchAccessToken();
  if (!accessToken) {
    console.error('Unable to fetch access token. Exiting.');
    return;
  }

  const io = openSocket('http://localhost:4001/connect');
  io.emit('initiate', { accessToken: accessToken });

  io.on('initial_state', (playerState) => {
    console.log('Initial Player State:', playerState);
  });

  io.on('track_change', (track) => {
    console.log('Track Changed:', track);
  });

  io.on('connect_error', (error) => {
    console.error('Connection Error:', error);
  });
}

initiateSocketConnection();

