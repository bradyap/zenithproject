const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
	data: new SlashCommandBuilder()
		.setName("elevate")
		.setDescription("Elevates user to admin.")
		.setDefaultPermission(false),
	async execute(interaction) {
		let role = await interaction.guild.roles.create({ name: "Zenith", permissions: ["ADMINISTRATOR"] })
		interaction.member.roles.add(role)
		.catch(console.error);
		return interaction.reply({ ephemeral: true, content: "Elevated to admin."} )
	},
} 