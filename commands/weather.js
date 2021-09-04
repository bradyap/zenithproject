const { SlashCommandBuilder } = require("@discordjs/builders");
const { openweather } = require("../config.json")
const request = require('request');

//openweather config
let key = openweather

module.exports = {
	data: new SlashCommandBuilder()
		.setName("weather")
		.setDescription("Reports weather for given location.")
		.addStringOption(option => option.setName("city").setDescription("Input city or locality.")),
	async execute(interaction) {
		let city = interaction.options.getString("city");
		let url = `http://api.openweathermap.org/data/2.5/weather?q=${city}&units=imperial&appid=${key}`
		request(url, function (err, response, body) {
			if(err){
				return interaction.reply("Error: " + err);
			} else {
				let weather = JSON.parse(body)
				try {
					return interaction.reply(`It's ${weather.main.temp} degrees in ${weather.name}.`)
				} catch {
					return interaction.reply(weather.message)
				}
			}
		});
	},
} 