var express = require("express");

var app = express();
var router = express.Router();

var port = process.env.PORT || 3000;

app.use("/", express.static(__dirname + "/public"));

app.listen(port);