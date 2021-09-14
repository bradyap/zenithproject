const fs = require("fs") 
const { Client, Collection, Intents } = require("discord.js") 
const { token } = require("./config.json") 

const client = new Client({ intents: [Intents.FLAGS.GUILDS] }) 

client.commands = new Collection() 
const commandFiles = fs.readdirSync("./commands").filter(file => file.endsWith(".js")) 

for (const file of commandFiles) {
	const command = require(`./commands/${file}`) 
	client.commands.set(command.data.name, command) 
}

client.once("ready", () => {
	console.log("Ready!")
	updatePermissions()
}) 

client.on("interactionCreate", async interaction => {
	if (!interaction.isCommand()) return 

	const command = client.commands.get(interaction.commandName) 

	if (!command) return 

	try {
		await command.execute(interaction) 
	} catch (error) {
		console.error(error) 
		return interaction.reply({ content: "There was an error while executing this command!", ephemeral: true }) 
	}
}) 

client.login(token) 

//update command permissions
async function updatePermissions() {
	
	await client.application?.fetch();

    //const command = await client.guilds.cache.get("760932362762059776")?.commands.fetch("882286487129964564");
	const command = await client.application?.commands.fetch("883574506491351082")
	const perms = [
        {
            id: "621056841606103042",
            type: "USER",
            permission: true,
        },
    ];
	const guilds = client.guilds.cache.map(guild => guild.id);
	for (const guild of guilds) {
		try {
			await command.permissions.set({ guild: guild, permissions: perms })
		} catch (error) {
			console.error(error)
		}
	}

    //await command.permissions.add({ permissions });
	
	console.log(command)
}