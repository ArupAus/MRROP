var express = require("express");
var	path = require("path");
var bodyParser = require("body-parser");

var index = require("./routes/index");

var app = express();

app.set("views",path.join(__dirname,"views"));
app.set("view engine","ejs");
app.use(express.static(__dirname + "/public"));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended:true}));

app.use("/",index);

// // HEROKU
//app.listen(process.env.PORT, process.env.IP, function(){
//   console.log("Heroku Server Started");
//});

// LOCAL HOST
app.listen(3000,function(){
	console.log("Server Started on PORT 3000");
})
