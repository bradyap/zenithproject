const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
	data: new SlashCommandBuilder()
		.setName("poll")
		.setDescription("Adds a vote to the previous message."),
	async execute(interaction) {
		interaction.channel.messages.fetch({ limit: 1 })
  		.then(messages => {
			let message = messages.first()
			let emotes = ["👍", "👎"]
			emotes.forEach(emote => message.react(emote))
		})
  		.catch(console.error);
		return interaction.reply({ ephemeral: true, content: "Vote added successfully."} )
	},
} 