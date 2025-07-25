import random
from . import main, cards, players, visuals
import discord
from discord import ui, Interaction, ButtonStyle
import asyncio
import pygame
import io


def renderGameStateBytes(window, last_played_card, player):
    deck_image = visuals.renderGameState(window, last_played_card, player)
    img_bytes = io.BytesIO()
    pygame.image.save(deck_image, img_bytes)
    img_bytes.seek(0)
    return img_bytes


def init(bot):
    @bot.command(
        name="infinunodeck",
        description="Display a random infinUno deck with a random starting card.",
    )
    async def infinUnoRandomDeckPreview(ctx):
        ctx.response.send_message()

    @bot.tree.command(name="infinuno")
    async def infinUno(ctx):
        """Starts the InfinUno game."""

        class JoinView(ui.View):
            def __init__(self, host):
                super().__init__(timeout=None)
                self.players = set()
                self.host = host
                self.join_button = ui.Button(
                    label="Join/Leave", style=ButtonStyle.primary
                )
                self.start_button = ui.Button(
                    label="Start", style=ButtonStyle.success, disabled=True
                )
                self.join_button.callback = self.join_callback
                self.start_button.callback = self.start_callback
                self.add_item(self.join_button)
                self.add_item(self.start_button)
                self.message = None

            async def join_callback(self, interaction: Interaction):
                user = interaction.user
                if user in self.players:
                    self.players.remove(user)  # type: ignore
                    await interaction.response.send_message(
                        "You left the game.", ephemeral=True
                    )
                else:
                    self.players.add(user)  # type: ignore
                    await interaction.response.send_message(
                        "You joined the game.", ephemeral=True
                    )
                self.start_button.disabled = (
                    len(self.players) == 0 or self.host not in self.players
                )
                await self.message.edit(view=self)  # type: ignore

            async def start_callback(self, interaction: Interaction):
                if interaction.user != self.host:
                    await interaction.response.send_message(
                        "Only the host can start the game.", ephemeral=True
                    )
                    return
                if len(self.players) == 0:
                    await interaction.response.send_message(
                        "No players have joined.", ephemeral=True
                    )
                    return
                # Start the game in a new task to continue independently of the start message
                asyncio.create_task(self.gameStart(interaction))
                self.stop()
                await self.message.edit(view=None)  # type: ignore

            async def gameStart(self, interaction):
                playerClasses = [players.Player(player) for player in self.players]
                self.players = playerClasses
                player_names = ", ".join(p.name for p in self.players)
                gameStartedMessage = f"Game started! {player_names}, check your DMs."
                await interaction.response.send_message(
                    gameStartedMessage, ephemeral=False
                )

                pygame.init()
                window = visuals.Window(
                    "InfinUno", pygame.display.set_mode((800, 600), pygame.HIDDEN)
                )
                last_played_card = random.choice(cards.ALL_CARDS)
                for player in self.players:
                    img_bytes = renderGameStateBytes(window, last_played_card, player)
                    await player.player.send(file=discord.File(img_bytes, filename="your_deck.png"))  # type: ignore
                pygame.quit()

        view = JoinView(ctx.user)
        await ctx.response.send_message(
            "Press **Join/Leave** to participate in InfinUno. The host can press **Start** when ready.",
            view=view,
        )
        view.message = await ctx.original_response()
