function getWeather() {
    const city = document.forms["weatherInput"]["city"].value;
    const output = document.getElementById("output");

    axios.get(`https://zenithproject.xyz/api/weather?locality=${city}`)
        .then(response => {
            weather = response.data
            var out = `The temperature in ${weather.name} is ${weather.main.temp.toFixed(0)}\u00B0F. The wind speed is ${weather.wind.speed} MPH and the humidity is ${weather.main.humidity}%.`
            output.value = out
            console.log("Weather fetched successfully. You can safely ignore the error message above.")
        })
        .catch(error => {
            output.value = "Working.."
            console.error(error.message)
        })

    
    
}   