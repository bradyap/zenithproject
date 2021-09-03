const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
	data: new SlashCommandBuilder()
		.setName("coinflip")
		.setDescription("Flips a coin."),
	async execute(interaction) {
		let num = math.random()
		if (num < 0.5) {
			return interaction.reply("It's heads!")
		} else {
			return interaction.reply("Tails.")
		}
	}
}