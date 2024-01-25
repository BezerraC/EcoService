import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

id_do_servidor = 941388532734361640 # Guild ID
id_cargo_atendente = 1072284447522685042 # Role ID 
id_suggestion = 1072589019726229625

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            # discord.SelectOption(value="help",label="Ajuda", emoji="👋"),
            discord.SelectOption(value="ticket",label="Ticket", emoji="📨"),
            discord.SelectOption(value="suggest",label="Send a Suggest", emoji="💡"),
            discord.SelectOption(value="bug",label="Bug Report", emoji="🐛"),
            discord.SelectOption(value="sponsor",label="Sponsor", emoji="🤝"),
        ]
        super().__init__(
            placeholder="Select an option...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_help"
        )
    async def callback(self, interaction: discord.Interaction):
        #if self.values[0] == "help":
            #await interaction.response.send_message("If you need help, coloque nos comentários do vídeo",ephemeral=True)
        if self.values[0] == "ticket":
            await interaction.response.send_message("Click below to create a ticket",ephemeral=True,view=CreateTicket())
            
        elif self.values[0] == "suggest":
            await interaction.response.send_message(f"To send a suggestion, use the command `/suggestion` ",ephemeral=True)
            
        elif self.values[0] == "bug":
            await interaction.response.send_message("To report a bug for one of our projects, follow these instructions:\n\nSend as much detail about it as possible (including description and photos).\n\nHaving this in hand, create a ticket below and send it.",ephemeral=True,view=CreateTicket())
            
        elif self.values[0] == "sponsor":
            await interaction.response.send_message("If you want to sponsor the eco community, you can make it with 2 ways.\n\n1 - Boosting the our server\n\n2 - Be a patrono [here](https://www.patreon.com/EcoBot791/membership) and unlock a most of content about us and receive more status",ephemeral=True)
            

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Dropdown())

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value=None

    @discord.ui.button(label="Open Ticket",style=discord.ButtonStyle.blurple,emoji="➕")
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True,content=f"You already have a call in progress!")
                    # await asyncio.sleep(10)
                    # await interaction.delete_original_response()
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_response(content=f"You already have a call in progress!",view=None)
                    # await asyncio.sleep(10)
                    # await interaction.delete_original_response()
                    return
        
        if ticket != None:
            await ticket.edit(archived=False)
            await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080,invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080)#,type=discord.ChannelType.public_thread)
            await ticket.edit(invitable=False)

        await interaction.response.send_message(ephemeral=True,content=f"I created a ticket for you! {ticket.mention}")
        # await asyncio.sleep(10)
        # await interaction.delete_original_response()
        
        await ticket.send(f"📩  **|** {interaction.user.mention} ticket created! Submit as much information as possible about your case and wait for an agent to respond.\n\nAfter your issue is resolved, you can use `/closeticket` to close the service!")



class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False #faz o bot não sincronizar os comandos mais de uma vez

    async def setup_hook(self) -> None:
        self.add_view(DropdownView())

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #Checar se os comandos slash foram sincronizados 
            await tree.sync(guild = discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Logging at - {self.user}.") 

aclient = client()

tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=id_do_servidor), name = 'setup', description='Setup')
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):

    embed = discord.Embed(
        colour = discord.Colour.blurple(),
        title = "Community Help Center",
        description = "In this section, you can contact our server team!. \n\nTo avoid problems, read the options carefully and remember to try to research your question before creating a service."
    )
    embed.set_image(url="https://i.postimg.cc/Kjc6qm4Y/Embed-Banner.png") #QxZN2HzF/EMBEDBANNER.png

    await interaction.response.send_message(embed=embed,view=DropdownView()) 


@tree.command(guild = discord.Object(id=id_do_servidor), name = 'suggestion', description='suggestion')
@app_commands.describe(suggestion = "Your suggestion")
async def suggest(interaction: discord.Interaction, suggestion: str):
    userAvatar = interaction.user.avatar.url
    embed = discord.Embed(
        title = f"New suggestion.",
        description = f"**By: {interaction.user}**\n\n{suggestion}",
        color = discord.Colour.blurple(),
    )
    embed.set_thumbnail(url=f'{userAvatar}')
    channel = aclient.get_channel(id_suggestion) #replace this with your own channel ID
    await channel.send(embed=embed)
    await interaction.response.send_message("Suggestion sent on channel <#1072589019726229625>")


@tree.command(guild = discord.Object(id=id_do_servidor), name="closeticket",description='Close a current service.')
async def _closeticket(interaction: discord.Interaction):
    mod = interaction.guild.get_role(id_cargo_atendente)
    if str(interaction.user.id) in interaction.channel.name or mod in interaction.author.roles:
        await interaction.response.send_message(f"The ticket was archived by {interaction.user.mention}, thank you for contacting us!")
        await interaction.channel.edit(archived=True)
    else:
        await interaction.response.send_message("It can't be done here...")


load_dotenv()
TOKEN = os.getenv('TOKEN')
aclient.run(TOKEN)