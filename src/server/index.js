var fs = require("fs");
var csv = require("csv");
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
  client.on('acceleration-request', function (data) {
    console.log(data);
    var options = Object.assign({args: [1, 50, "test.csv"]}, pythonShellOptions);
      PythonShell.run('adxl345-test.py', options, (err, results) => {
        if(err) {
          console.log(err);
          throw err;
        }
        console.log(results);
        var values = results[0].split(",");
        var numberOfSamples = 50;
        var startTime = 0;
        var endTime = 0;
        if (values.length >= 5) {
          startTime = values[0];
          endTime = values[1];
          numberOfSamples = values[4];
        }
        var interval = (endTime - startTime) * 1.00 / numberOfSamples;

        var parser = csv.parse({ delimiter: "," }, function (err, data) {
          // csv.from.path(__dirname + "/test.csv").to.array(function (data) {
          var dataWithTime = [];
          data.forEach((d, i) => {
            dataWithTime.push([(+startTime) + i * interval].concat(data[i]));
          })
          client.emit("acceleration-response", dataWithTime);
          fs.unlink("./test.csv", function (err) {
            if (!err) console.log("file removed");
            else console.log(err);
          });
        });
        fs.createReadStream("./test.csv").pipe(parser);
        console.log(results);
      }); 
   });
  client.on('fft-request', function (data) {
    console.log(data);
    var options = Object.assign({args: [1, 50, "fft.csv"]}, pythonShellOptions);
      PythonShell.run('adxl345-fft-test.py', options, (err, results) => {
        if(err) {
          console.log(err);
          throw err;
        }
        console.log(results);
        var values = results[0].split(",");
        var numberOfSamples = 50;
        var startTime = 0;
        var endTime = 0;
        if (values.length >= 5) {
          startTime = values[0];
          endTime = values[1];
          numberOfSamples = values[4];
        }
        var interval = (endTime - startTime) * 1.00 / numberOfSamples;

        var parser = csv.parse({ delimiter: "," }, function (err, data) {
          // csv.from.path(__dirname + "/fft.csv").to.array(function (data) {
          var dataFFT = data.slice(1);
          client.emit("acceleration-response", dataFFT);
          fs.unlink("./fft.csv", function (err) {
            if (!err) console.log("file removed");
            else console.log(err);
          });
        });
        fs.createReadStream("./fft.csv").pipe(parser);
        console.log(results);
      }); 
   });
  client.on('disconnect', function () {
    console.log("disconnected ", client.id);
  });
});
io.listen(3000);

