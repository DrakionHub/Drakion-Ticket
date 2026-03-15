import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import datetime
import os

TOKEN = os.getenv("TOKEN1")

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
# MODAL PARA CRIAR TICKET
# =========================

class TicketReasonModal(Modal, title="Criar Ticket"):

    motivo = TextInput(
        label="Motivo do ticket",
        placeholder="Explique o problema...",
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

        tickets[channel.id] = {
            "user": user.id,
            "reason": self.motivo.value,
            "created": datetime.datetime.now()
        }

        await channel.set_permissions(user, read_messages=True, send_messages=True)

        embed = discord.Embed(
            title="Suporte | Ticket",
            description=f"Olá {user.mention}",
            color=0xff0000
        )

        embed.add_field(
            name="Motivo",
            value=self.motivo.value,
            inline=False
        )

        embed.add_field(
            name="Status",
            value="Aberto",
            inline=True
        )

        embed.set_footer(text="Drakion Ticket")

        await channel.send(
            content=f"{user.mention}",
            embed=embed,
            view=TicketButtons()
        )

        log = bot.get_channel(LOG_CREATE)

        embedlog = discord.Embed(
            title="Ticket Criado",
            color=0x00ff00
        )

        embedlog.add_field(name="Usuário", value=user.mention)
        embedlog.add_field(name="Motivo", value=self.motivo.value)

        await log.send(embed=embedlog)

        await interaction.response.send_message(
            f"Ticket criado: {channel.mention}",
            ephemeral=True
        )


# =========================
# MODAL PARA FECHAR TICKET
# =========================

class CloseModal(Modal, title="Fechar Ticket"):

    motivo = TextInput(
        label="Motivo do fechamento",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.channel

        data = tickets.get(channel.id)

        user = interaction.guild.get_member(data["user"])

        transcript = f"https://nshw.squareweb.app/transcript/{interaction.guild.id}/{channel.id}"

        log = bot.get_channel(LOG_CLOSE)

        embed = discord.Embed(
            title="Ticket Fechado",
            color=0xff0000
        )

        embed.add_field(name="Usuário", value=user.mention)
        embed.add_field(name="Staff", value=interaction.user.mention)
        embed.add_field(name="Motivo", value=self.motivo.value)

        view = View()
        view.add_item(Button(label="Transcript", url=transcript))

        await log.send(embed=embed, view=view)

        try:
            await user.send(embed=embed, view=view)
        except:
            pass

        await interaction.response.send_message("Ticket será fechado.")

        await channel.delete()


# =========================
# BOTÕES DO TICKET
# =========================

class TicketButtons(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Assumir Ticket", style=discord.ButtonStyle.green)
    async def assumir(self, interaction: discord.Interaction, button: Button):

        if not any(role.id in STAFF_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        embed = discord.Embed(
            description=f"Ticket assumido por {interaction.user.mention}",
            color=0x00ff00
        )

        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Finalizar Ticket", style=discord.ButtonStyle.red)
    async def fechar(self, interaction: discord.Interaction, button: Button):

        if not any(role.id in STAFF_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        await interaction.response.send_modal(CloseModal())


# =========================
# BOTÃO PRINCIPAL
# =========================

class TicketPanel(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir Ticket",
        style=discord.ButtonStyle.primary,
        custom_id="open_ticket"
    )
    async def ticket(self, interaction: discord.Interaction, button: Button):

        await interaction.response.send_modal(TicketReasonModal())


# =========================
# COMANDO PARA ENVIAR PAINEL
# =========================

@bot.tree.command(name="ticket_panel")
async def painel(interaction: discord.Interaction):

    if not any(role.id == COMMAND_ROLE for role in interaction.user.roles):
        return await interaction.response.send_message(
            "Sem permissão.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Suporte",
        description="Clique no botão abaixo para abrir um ticket.",
        color=0xff0000
    )

    await interaction.channel.send(embed=embed, view=TicketPanel())

    await interaction.response.send_message(
        "Painel enviado.",
        ephemeral=True
    )


# =========================

@bot.event
async def on_ready():

    bot.add_view(TicketPanel())
    bot.add_view(TicketButtons())

    await bot.tree.sync()

    print("Bot online")


bot.run(TOKEN1)
