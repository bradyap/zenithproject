const axios = require('axios').default;

const { openweather } = require("../../../config.json")

//openweather api key
const key = openweather

module.exports = {
	getWeather: function (locality) {
		var url = `http://api.openweathermap.org/data/2.5/weather?q=${locality}&units=imperial&appid=${key}`
		return axios.get(url)
	}
}