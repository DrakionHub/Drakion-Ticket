import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os
import datetime

TOKEN = os.getenv("TOKEN1")

GUILD_ID = 1481089628374171651

TICKET_CATEGORY = 1482794919272779990
LOG_CREATE = 1482788464876585070
LOG_CLOSE = 1482789079375675433

STAFF_ROLES = [
1482423776158154953,
1482425821460304144,
1481089914522173520,
1482425697736589604
]

COMMAND_ROLE = 1482423776158154953

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

tickets = {}

# =========================
# MODAL CRIAR TICKET
# =========================

class TicketModal(Modal, title="Create Ticket"):

    reason = TextInput(
        label="Reason",
        placeholder="Explain your problem...",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY)
        user = interaction.user

        created_time = datetime.datetime.now()
        formatted_time = created_time.strftime("%d/%m/%Y %H:%M")

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )

        await channel.set_permissions(user, read_messages=True, send_messages=True)

        tickets[channel.id] = {
            "user": user.id,
            "reason": self.reason.value,
            "created": formatted_time,
            "claimed_by": None
        }

        embed = discord.Embed(
            title=f"Hello {user.name} 👋, We are at your service.",
            description=f"🇺🇸 A staff member will assist you shortly. Please provide all necessary information about your issue to help us assist you better.\n\n🇧🇷 Um membro da nossa equipe irá atendê-lo em breve. Por favor, forneça todas as informações necessárias sobre o seu problema para que possamos ajudá-lo da melhor forma possível.\n\n",
            color=0xff0000
        )

        embed.add_field(name="`Motive:`", value=self.reason.value, inline=False)
        embed.add_field(name="`Created at:`", value=formatted_time, inline=False)
        embed.add_field(name="`Assumed by:`", value="Ticket not claimed", inline=False)
        embed.set_footer(text= "Drakion Ticket © | All Rights Reserved.", icon_url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048") 
        embed.set_image(url="https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048")  # Adicione esta linha para a thumbnail
    
        await channel.send(
            content=f"{user.mention} <@&1482826480248553584>",
            embed=embed,
            view=TicketButtons()
        )

        log = bot.get_channel(LOG_CREATE)

        embedlog = discord.Embed(
            title="Ticket Created",
            color=0x00ff00
        )

        embedlog.add_field(name="User", value=user.mention, inline=False)
        embedlog.add_field(name="Reason", value=self.reason.value, inline=False)
        embedlog.add_field(name="Created at", value=formatted_time, inline=False)
        embedlog.add_field(name="Channel", value=channel.mention, inline=False)

        await log.send(embed=embedlog)

        await interaction.response.send_message(
            f"Ticket created: {channel.mention}",
            ephemeral=True
        )

# =========================
# MODAL FECHAR TICKET
# =========================

class CloseModal(Modal, title="Close Ticket"):

    reason = TextInput(
        label="Reason for closing",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.channel
        data = tickets.get(channel.id)

        user = interaction.guild.get_member(data["user"])

        closed_time = datetime.datetime.now()
        formatted_close = closed_time.strftime("%d/%m/%Y %H:%M")

        log = bot.get_channel(LOG_CLOSE)

        embed = discord.Embed(
            title="Ticket Closed",
            color=0xff0000
        )

        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Closed by", value=interaction.user.mention, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="Closed at", value=formatted_close, inline=False)

        await log.send(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="Your ticket was closed",
                color=0xff0000
            )

            dm_embed.add_field(name="Closed by", value=interaction.user.mention, inline=False)
            dm_embed.add_field(name="Reason", value=self.reason.value, inline=False)
            dm_embed.add_field(name="Closed at", value=formatted_close, inline=False)

            await user.send(embed=dm_embed)

        except:
            pass

        await interaction.response.send_message("Closing ticket...")

        await channel.delete()

# =========================
# BOTÕES DO TICKET
# =========================

class TicketButtons(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: Button):

        if not any(role.id in STAFF_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        channel = interaction.channel
        data = tickets.get(channel.id)

        if data["claimed_by"] is not None:
            staff = interaction.guild.get_member(data["claimed_by"])
            return await interaction.response.send_message(
                f"This ticket has already been claimed by {staff.mention}.",
                ephemeral=True
            )

        data["claimed_by"] = interaction.user.id

        message = interaction.message
        embed = message.embeds[0]

        embed.set_field_at(
            2,
            name="`Assumed by:`",
            value=interaction.user.mention,
            inline=False
        )

        await message.edit(embed=embed)

        await interaction.response.send_message(
            f"Ticket claimed by {interaction.user.mention}"
        )

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: Button):

        if not any(role.id in STAFF_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        await interaction.response.send_modal(CloseModal())

# =========================
# PAINEL DE TICKET
# =========================

class TicketPanel(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Open Ticket",
        style=discord.ButtonStyle.primary,
        custom_id="open_ticket"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: Button):

        await interaction.response.send_modal(TicketModal())

# =========================
# COMANDO /ticket_panel
# =========================

@bot.tree.command(name="ticket_panel", description="Send the ticket panel")
async def ticket_panel(interaction: discord.Interaction):

    if not any(role.id == COMMAND_ROLE for role in interaction.user.roles):
        return await interaction.response.send_message(
            "You don't have permission.",
            ephemeral=True
        )

    embed = discord.Embed(
    title="🐉 Service | Drakion Support",
    description="""🇺🇸  ⚠️ Before opening a ticket:\n\n• Describe your issue clearly and briefly.\n• Avoid mentioning or pinging staff members.\n• Please be patient while waiting for a response.\n• Tickets without activity may be closed automatically.\n• Misuse of the support system may result in punishments.\n\n➡️ After opening the ticket, explain your situation and a staff member will assist you in the ticket.\n\n🇧🇷  ⚠️ Antes de abrir um ticket:\n• Descreva seu problema de forma clara e objetiva.\n• Evite marcar ou mencionar membros da equipe.\n• Aguarde a resposta da staff com paciência.\n• Tickets sem atividade podem ser encerrados automaticamente.\n• Uso indevido do sistema de suporte pode resultar em punições.\n\n➡️ Após abrir o ticket, explique sua situação e um membro da equipe irá ajudá-lo no próprio atendimento.""",
    color=0xff0000
)

    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048")  # Adicione esta linha para a thumbnail
    embed.set_image(url="https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png")
    embed.set_footer(text= "Drakion Ticket © | All Rights Reserved.", icon_url="https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048") 

    await interaction.channel.send(embed=embed, view=TicketPanel())

    await interaction.response.send_message(
        "Ticket panel sent.",
        ephemeral=True
    )

# =========================
# READY
# =========================

@bot.event
async def on_ready():

    guild = discord.Object(id=GUILD_ID)

    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

    bot.add_view(TicketPanel())
    bot.add_view(TicketButtons())

    print("Bot online and commands synced")

bot.run(TOKEN)
