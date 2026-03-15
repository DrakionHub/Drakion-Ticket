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

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )

        await channel.set_permissions(user, read_messages=True, send_messages=True)

        tickets[channel.id] = {
            "user": user.id,
            "reason": self.reason.value,
            "created": datetime.datetime.now()
        }

        embed = discord.Embed(
            title="Support Ticket",
            description=f"{user.mention} opened a ticket",
            color=0xff0000
        )

        embed.add_field(
            name="Reason",
            value=self.reason.value,
            inline=False
        )

        await channel.send(
            content=user.mention,
            embed=embed,
            view=TicketButtons()
        )

        log = bot.get_channel(LOG_CREATE)

        embedlog = discord.Embed(
            title="Ticket Created",
            color=0x00ff00
        )

        embedlog.add_field(name="User", value=user.mention)
        embedlog.add_field(name="Reason", value=self.reason.value)

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

        log = bot.get_channel(LOG_CLOSE)

        embed = discord.Embed(
            title="Ticket Closed",
            color=0xff0000
        )

        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Closed by", value=interaction.user.mention)
        embed.add_field(name="Reason", value=self.reason.value)

        await log.send(embed=embed)

        try:
            await user.send(embed=embed)
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

        embed = discord.Embed(
            description=f"Ticket claimed by {interaction.user.mention}",
            color=0x00ff00
        )

        await interaction.response.send_message(embed=embed)

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
        title="Support",
        description="Click the button below to open a support ticket.",
        color=0xff0000
    )

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

    guild = discord.Object(id=1481089628374171651)

    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

    bot.add_view(TicketPanel())
    bot.add_view(TicketButtons())

    print("Bot is online and commands synced")


bot.run(TOKEN)
