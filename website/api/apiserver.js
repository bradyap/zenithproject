const express = require("express");

const app = express()

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

//modules
const weather = require("./api/weather");

app.get("/api/", (req, res) => {
    res.send("Available.")
});

app.get("/api/weather/", (req, res) => {
    var locality = req.query.locality
    weather.getWeather(locality)
        .then(response => {
            res.send(response.data)
        })
        .catch(error => {
            res.send(error.message)
        })
});

app.listen(3000, () => console.log("Listening.."))