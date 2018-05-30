// with ES6 import
const io=require('socket.io-client');
const socket = io('http://localhost:3000');
socket.emit('acceleration-request', { durationInSeconds: 5, rateInHz: 25});
socket.on('acceleration-response', (data) => {
  console.log(data);
});
socket.emit('fft-request', { durationInSeconds: 5, rateInHz: 25});
socket.on('fft-response', (data) => {
  console.log(data);
});

