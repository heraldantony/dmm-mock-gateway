// with ES6 import
const io=require('socket.io-client');
const socket = io('http://localhost:3000');
socket.emit('data-request', { durationInSeconds: 5, rateInHz: 25});
socket.on('data-response', (data) => {
  console.log(data);
});

