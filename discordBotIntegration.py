import random
from . import main, cards, players, visuals
import discord
from discord import ui, Interaction, ButtonStyle
import asyncio
import pygame
import io
from PIL import Image


def renderGameStateBytes(window, last_played_card, player):
    deck_image = visuals.renderGameState(window, last_played_card, player)
    # Convert pygame surface to string buffer
    data = pygame.image.tostring(deck_image, "RGBA")
    size = deck_image.get_size()
    # Create PIL Image
    image = Image.frombytes("RGBA", size, data)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


def init(bot):
    @bot.command(
        name="infinunodeck",
        description="Display a random infinUno deck with a random starting card.",
    )
    async def infinUnoRandomDeckPreview(ctx):
        """Generates a random deck and sends it as an image."""
        last_played_card = random.choice(cards.ALL_CARDS)  # Randomly select a card
        window = visuals.Window(
            "InfinUno Deck Preview", pygame.display.set_mode((800, 600), pygame.HIDDEN)
        )
        img_bytes = renderGameStateBytes(window, last_played_card, players.Player())
        await ctx.send(file=discord.File(img_bytes, filename="your_deck.png"))

    @bot.tree.command(name="infinuno")
    async def infinUno(ctx):
        """Starts the InfinUno game."""

        class JoinView(ui.View):
            class LeaveView(ui.View):
                def __init__(self, parent, player):
                    super().__init__(timeout=None)
                    self.parent = parent
                    self.player = player
                    self.leave_button = ui.Button(label="Leave", style=ButtonStyle.danger)
                    self.leave_button.callback = self.leave_callback
                    self.add_item(self.leave_button)
                    self.message = None

                async def leave_callback(self, interaction: Interaction):
                    if hasattr(self.player, 'player') and interaction.user != self.player.player:
                        await interaction.response.send_message("You can only leave your own game.", ephemeral=True)
                        return
                    # Remove player from game
                    self.parent.players = [p for p in self.parent.players if p != self.player]
                    await interaction.response.send_message("You have left the game.", ephemeral=True)
                    if self.message:
                        result = self.message.edit(content="You have left the game.", attachments=[], view=None)
                        if asyncio.iscoroutine(result):
                            try:
                                await result # type: ignore
                            except Exception:
                                pass
            def __init__(self, host):
                super().__init__(timeout=None)
                self.players = []
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
                    self.players.append(user)  # type: ignore
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
                try:
                    await interaction.response.send_message(
                        gameStartedMessage, ephemeral=False
                    )
                except discord.errors.InteractionResponded:
                    await interaction.channel.send(gameStartedMessage)

                pygame.init()
                self.window = visuals.Window(
                    "InfinUno", pygame.display.set_mode((800, 600), pygame.HIDDEN)
                )
                self.last_played_card = random.choice(cards.ALL_CARDS)
                self.nextMessageContent = ""
                self.current_player_index = (
                    -1
                )  # Since the last card was played by the game itself
                self.num_players = len(self.players)
                self.drawCounter = 0

                try:
                    self.last_played_card.affects.remove(0)  # Remove the game itself from affects of this first card
                except ValueError:
                    pass

                self.drawCounter += self.last_played_card.add  # add first, then multiply for more adding influence when also multiplying
                self.drawCounter *= self.last_played_card.mult
                self.drawCounter = int(self.drawCounter)  # Ensure drawCounter is an integer

                # Send initial deck image to all players with leave button
                for player in self.players:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, player
                    )
                    leave_view = self.LeaveView(self, player)
                    player.deck_message = await player.player.send(  # type: ignore
                        file=discord.File(img_bytes, filename="your_deck.png"),
                        view=leave_view
                    )
                    leave_view.message = player.deck_message # type: ignore

                gameFinished = False
                while not gameFinished:
                    gameFinished = await self.gameTick()

                print(f"{player_names}: Game of infinUno finished.")
                await self.show_restart_button(interaction)
                pygame.quit()

            async def show_restart_button(self, interaction):
                class RestartView(ui.View):
                    def __init__(self, parent):
                        super().__init__(timeout=None)
                        self.parent = parent
                        self.restart_button = ui.Button(label="Restart Game", style=ButtonStyle.success)
                        self.restart_button.callback = self.restart_callback
                        self.add_item(self.restart_button)
                        self.message = None

                    async def restart_callback(self, interaction: Interaction):
                        if interaction.user != self.parent.host:
                            await interaction.response.send_message("Only the host can restart the game.", ephemeral=True)
                            return
                        await interaction.response.defer()
                        # Restart the game with the same players
                        self.parent.players = [p.player if hasattr(p, 'player') else p for p in self.parent.players]
                        asyncio.create_task(self.parent.gameStart(interaction))
                        self.stop()
                        await self.message.edit(view=None) # type: ignore

                view = RestartView(self)
                msg = await interaction.channel.send(f"Game finished! Host can restart the game.", view=view)
                view.message = msg

            async def gameTick(self):
                self.nextMessageContent = ""
                gameFinished = False
                current_player = self.players[self.current_player_index]

                # Gather all target players affected by the last played card
                target_players = []
                for offset in self.last_played_card.affects:
                    target_index = (
                        self.current_player_index + offset
                    ) % self.num_players
                    target_players.append(self.players[target_index])

                # Handle stacking draw cards
                if self.drawCounter != 0:
                    self.nextMessageContent += f"\nThere was an existing draw counter of {self.drawCounter}."
                    stackableFound = False
                    for target in target_players:
                        # Find stackable cards in target's hand
                        stackable = []
                        for c in target.hand.cards:
                            if c.add != 0 or c.mult != 1.0:
                                stackable.append(c)
                        if stackable:
                            # Let the player stack (this is a placeholder for actual interaction)
                            # later, we'll prompt the player to play a stackable card
                            # For now, just play the first stackable card
                            played_card = stackable[0]
                            self.nextMessageContent += f"\nYou automatically played your first stackable card: {played_card.name}."
                            target.hand.remove(played_card)
                            self.last_played_card = played_card
                            # Update drawCounter
                            self.drawCounter = int(
                                (self.drawCounter + played_card.add) * played_card.mult  # add first, then multiply for more adding influence when also multiplying
                            )
                            self.nextMessageContent += f"\nThe draw counter is now {self.drawCounter}."
                            stackableFound = True
                            break
                    if not stackableFound:
                        for target in target_players:
                            target.hand.draw(self.drawCounter)
                            self.drawCounter = 0  # Reset draw counter
                        self.nextMessageContent += f"\n{", ".join([target.name for target in target_players])} drew {self.drawCounter} cards."

                # Check skip indicator
                if self.last_played_card.skip and current_player in target_players:
                    self.nextMessageContent += f"\nYou were skipped."
                    # we just got skipped. Because this card will also be the last played card for the next player, we must adjust the affects of this card by pushing every value down by one
                    self.last_played_card.affects = [a - 1 for a in self.last_played_card.affects if a - 1 >= 0]
                    # we remove negative values, because with more players, the probability of this card laying long enough to skip someone from the end of the list decreases enough for us to just not respect you playing it.
                    # DO NOT remove removing negative values, as that will cause the game to get stuck in an infinite loop when there are not more players than affected targets.
                else:
                    # enable the current player to play a card
                    self.nextMessageContent += f"\nYou may now play a card. (But for now, the game ends here.)"
                    gameFinished = True # For now, we end the game as soon as a card can be played by the player

                # Send update deck image to the current player
                if self.current_player_index >= 0:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, current_player
                    )
                    leave_view = self.LeaveView(self, current_player)
                    msg = await current_player.player.send( # type: ignore
                        file=discord.File(img_bytes, filename="your_deck.png"),
                        view=leave_view
                    )
                    setattr(current_player, 'deck_message', msg)
                    leave_view.message = msg

                # Send updated deck image to all target players
                for player in target_players:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, player
                    )
                    leave_view = self.LeaveView(self, player)
                    # Instead of sending a new message, edit the previous one with the updated image and leave button
                    if hasattr(player, "deck_message") and player.deck_message:
                        await player.deck_message.edit(content=f"{self.nextMessageContent}", attachments=[discord.File(img_bytes, filename="your_deck.png")], view=leave_view)
                        leave_view.message = player.deck_message
                    else:
                        msg = await player.player.send(content=f"This is your deck.{self.nextMessageContent}", file=discord.File(img_bytes, filename="your_deck.png"), view=leave_view)  # type: ignore
                        setattr(player, 'deck_message', msg)
                        leave_view.message = msg

                # Update current player index for the next turn
                self.current_player_index = (self.current_player_index + 1) % self.num_players
                return gameFinished

        view = JoinView(ctx.user)
        await ctx.response.send_message(
            "Press **Join/Leave** to participate in InfinUno. The host can press **Start** when ready.",
            view=view,
        )
        view.message = await ctx.original_response()
