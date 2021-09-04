const { SlashCommandBuilder } = require("@discordjs/builders");
const { openweather } = require("../config.json")
const request = require('request');
const { MessageEmbed } = require('discord.js');

//openweather config
let key = openweather

module.exports = {
	data: new SlashCommandBuilder()
		.setName("weather")
		.setDescription("Reports weather for given location.")
		.addStringOption(option => option.setName("city").setDescription("City or locality."))
		.addIntegerOption(option => option.setName("zip").setDescription("ZIP code.")),
	async execute(interaction) {
		if (interaction.options.getString("city")) {
			var locality = interaction.options.getString("city")
			var url = `http://api.openweathermap.org/data/2.5/weather?q=${locality}&units=imperial&appid=${key}`
		} else if (interaction.options.getInteger("zip")) {
			var locality = interaction.options.getInteger("zip")
			var url = `http://api.openweathermap.org/data/2.5/weather?zip=${locality}&units=imperial&appid=${key}`
		} else {
			return interaction.reply("Please enter a city or ZIP code.");
		}
		request(url, function (err, response, body) {
			if(err){
				return interaction.reply("Error: " + err);
			} else {
				let weather = JSON.parse(body)
				if (weather.main) {
					//parse sunrise time
					let sunrise = {}
					sunrise.date = new Date((weather.sys.sunrise + weather.timezone) * 1000) //date object
					sunrise.suffix = sunrise.date.getHours() >= 12 ? "PM" : "AM" //determines whether time is AM or PM
					sunrise.hours = (sunrise.date.getHours() % 12) || 12 //converts from 24 to 12 hour time
					sunrise.minutes = sunrise.date.getMinutes() <= 9 ? `0${sunrise.date.getMinutes()}` : sunrise.date.getMinutes() //adds 0 if minutes are less than 10
					sunrise.string = (`${sunrise.hours}:${sunrise.minutes} ${sunrise.suffix}`) //assembles time into string
					//parse sunset time
					let sunset = {}
					sunset.date = new Date((weather.sys.sunset + weather.timezone) * 1000) //date object
					sunset.suffix = sunset.date.getHours() >= 12 ? "PM" : "AM" //determines whether time is AM or PM
					sunset.hours = (sunset.date.getHours() % 12) || 12 //converts from 24 to 12 hour time
					sunset.minutes = sunset.date.getMinutes() <= 9 ? `0${sunset.date.getMinutes()}` : sunset.date.getMinutes() //adds 0 if minutes are less than 10
					sunset.string = (`${sunset.hours}:${sunset.minutes} ${sunset.suffix}`) //assembles time into string
					let embed = new MessageEmbed()
						.setTitle(`Weather report for ${weather.name}`)
						.setThumbnail("https://static.thenounproject.com/png/259207-200.png")
						.setDescription(`${capitalize(weather.weather[0].description)}.`)
						.addFields(
							{ name: "🌡️ Temperature (Feels Like)", value: `${weather.main.temp.toFixed(0)}\u00B0F (${weather.main.feels_like.toFixed(0)}\u00B0F)` },
							{ name: "🔥 Max Temp", value: `${weather.main.temp_max.toFixed(0)}\u00B0F`, inline:true },
							{ name: "☀️ Sunrise", value: sunrise.string, inline: true },
							{ name: "💨 Wind Speed", value: `${weather.wind.speed} MPH`, inline:true },
							{ name: "🧊 Min Temp", value: `${weather.main.temp_min.toFixed(0)}\u00B0F`, inline:true },
							{ name: "🌙 Sunset", value: sunset.string, inline: true },
							{ name: "💧 Humidity", value: `${weather.main.humidity}%`, inline:true }
						)
						.setTimestamp()
					return interaction.reply({ embeds: [embed] });
				} else {
					return interaction.reply(`Locality "${locality}" not found. Try a nearby major city or town or enter a valid ZIP code.`)
				}
			}
		});
	},
} 

//capitalize first letter of string
function capitalize(string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}