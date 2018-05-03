var webpack = require("webpack");
var path = require("path");
var fs = require("fs");

var nodeModules = {};
fs
  .readdirSync("node_modules")
  .filter(function(x) {
    return [".bin"].indexOf(x) === -1;
  })
  .forEach(function(mod) {
    nodeModules[mod] = "commonjs " + mod;
  });
module.exports = {
  target: "node",
  externals: nodeModules,
  entry: {
     server: "src/server/index.js",
     client: "src/client/index.js"
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  }
};
