function getWeather() {
    const http = new XMLHttpRequest();
    const key = "fc8f38f90c53dc140105740bb3719a59"
    const city = document.forms["weatherInput"]["city"].value;
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&units=imperial&appid=${key}`
    const output = document.getElementById("output");

    http.onreadystatechange = function() {
        if (http.readyState === XMLHttpRequest.DONE) {
            if (http.status === 200) {
                let weather = JSON.parse(http.responseText);
                var out = `The temperature in ${weather.name} is ${weather.main.temp.toFixed(0)}\u00B0F. The wind speed is ${weather.wind.speed} MPH and the humidity is ${weather.main.humidity}%`
                output.value = out
            } else {
                output.value = "City or locality not found.";
            }
        } else {
            output.value = "Fetching weather.."
        }
    }
    http.open("GET", url);
    http.send();
    
}   