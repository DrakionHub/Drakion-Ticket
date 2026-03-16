import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os
import datetime
import chat_exporter
from zoneinfo import ZoneInfo
import asyncio

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
        label="Motive for opening the ticket",
        placeholder="Explain your problem...",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY)
        user = interaction.user

        for ticket in tickets.values():
            if ticket["user"] == user.id:
                return await interaction.response.send_message(
                    "You already have an open ticket.",
                    ephemeral=True
                )

        created_time = datetime.datetime.now(ZoneInfo('America/Sao_Paulo'))
        formatted_time = created_time.strftime("%d/%m/%Y %H:%M (Brasília time - BR)")

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
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
            title=f"Hello {user.name} 👋",
            description="A staff member will assist you shortly.",
            color=0xff0000
        )

        embed.add_field(name="Motive", value=self.reason.value, inline=False)
        embed.add_field(name="Created at", value=formatted_time, inline=False)
        embed.add_field(name="Assumed by", value="Ticket not claimed", inline=False)

        await channel.send(
            content=f"{user.mention}",
            embed=embed,
            view=TicketButtons()
        )

        log = bot.get_channel(LOG_CREATE)

        embedlog = discord.Embed(
            title="Ticket Created",
            color=0xff0000
        )

        embedlog.add_field(name="User", value=user.mention, inline=False)
        embedlog.add_field(name="Motive", value=self.reason.value, inline=False)
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

        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        data = tickets.get(channel.id)

        if data is None:
            return await interaction.followup.send(
                "Ticket data not found.",
                ephemeral=True
            )

        user = interaction.guild.get_member(data["user"])

        if user is None:
            user = await bot.fetch_user(data["user"])

        closed_time = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
        formatted_close = closed_time.strftime("%d/%m/%Y %H:%M")

        transcript_url = None

        try:

            transcript = await chat_exporter.export(
                channel,
                limit=None,
                tz_info="America/Sao_Paulo",
                guild=interaction.guild,
                bot=bot
            )

            if transcript:

                os.makedirs("transcripts", exist_ok=True)

                file_name = f"{interaction.guild.id}-{channel.id}.html"
                file_path = f"transcripts/{file_name}"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(transcript)

                transcript_url = f"https://Drakionbot.up.railway.app/transcript/{file_name}"

                print("Transcript created:", transcript_url)

        except Exception as e:
            print("Transcript error:", e)

        embed = discord.Embed(
            title="Ticket Closed",
            color=0xff0000
        )

        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Closed by", value=interaction.user.mention, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="Closed at", value=formatted_close, inline=False)

        view = View()

        if transcript_url:
            view.add_item(
                Button(
                    label="View Transcript",
                    style=discord.ButtonStyle.link,
                    url=transcript_url
                )
            )

        log = bot.get_channel(LOG_CLOSE)

        await log.send(embed=embed, view=view)

        try:
            await user.send(embed=embed, view=view)
        except:
            pass

        await interaction.followup.send("Closing ticket...")

        tickets.pop(channel.id, None)

        await asyncio.sleep(2)
        await channel.delete()

# =========================
# BOTÕES DO TICKET
# =========================

class TicketButtons(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: Button):

        if not any(role.id in STAFF_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        data = tickets.get(interaction.channel.id)

        if data["claimed_by"]:
            return await interaction.response.send_message(
                "Ticket already claimed.",
                ephemeral=True
            )

        data["claimed_by"] = interaction.user.id

        await interaction.response.send_message(
            f"Ticket claimed by {interaction.user.mention}"
        )

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):

        if not any(role.id in STAFF_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        await interaction.response.send_modal(CloseModal())

# =========================
# PAINEL
# =========================

class TicketPanel(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, button: Button):

        await interaction.response.send_modal(TicketModal())

# =========================
# COMANDO
# =========================

@bot.tree.command(name="ticket_panel", description="Send the ticket panel")
async def ticket_panel(interaction: discord.Interaction):

    if not any(role.id == COMMAND_ROLE for role in interaction.user.roles):
        return await interaction.response.send_message(
            "You don't have permission.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Drakion Support",
        description="Click below to open a support ticket.",
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

    guild = discord.Object(id=GUILD_ID)

    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

    bot.add_view(TicketPanel())
    bot.add_view(TicketButtons())

    print("Bot online")

bot.run(TOKEN)
