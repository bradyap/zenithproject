const express = require("express");
const path = require("path")

const app = express()

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "./html/index.html"))
});

app.listen(3030, () => console.log("Listening.."))