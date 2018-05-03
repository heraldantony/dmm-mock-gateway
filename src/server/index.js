var io = require('socket.io')();
var pythonShellOptions = {
  mode: 'text',
  pythonOptions: ['-u'], // get print results in real-time
  scriptPath: './adxl345'
}
var PythonShell = require('python-shell');
var port = process.env.PORT || 3000;

io.on('connection', function (client) {
  console.log("connected ", client.id);
  client.on('data-request', function (data) {
    console.log(data);
    var options = Object.assign({args: [1, 50, "test.out"]}, pythonShellOptions);
      PythonShell.run('adxl345-test.py', options, (err, results) => {
        if(err) {
          console.log(err);
          throw err;
        }
        console.log(results);
        client.emit('data-response', results);
      }); 
   });
  client.on('disconnect', function () {
    console.log("disconnected ", client.id);
  });
});
io.listen(3000);

