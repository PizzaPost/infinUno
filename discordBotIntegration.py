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
                    self.leave_button = ui.Button(
                        label="Leave", style=ButtonStyle.danger
                    )
                    self.leave_button.callback = self.leave_callback
                    self.add_item(self.leave_button)
                    self.message = None

                async def leave_callback(self, interaction: Interaction):
                    if (
                        hasattr(self.player, "player")
                        and interaction.user != self.player.player
                    ):
                        await interaction.response.send_message(
                            "You can only leave your own game.", ephemeral=True
                        )
                        return
                    # Remove player from game
                    self.parent.players = [
                        p for p in self.parent.players if p != self.player
                    ]
                    if self.message:
                        result = self.message.edit(
                            content="You have left the game.", attachments=[], view=None
                        )
                        if asyncio.iscoroutine(result):
                            try:
                                await result  # type: ignore
                            except Exception:
                                pass
                    # Host left: assign new host if possible, else abort
                    if self.parent.host == self.player:
                        if len(self.parent.players) >= 2:
                            import random

                            self.parent.host = random.choice(self.parent.players)
                            if self.parent.message:
                                await self.parent.message.edit(
                                    content=f"Host has left. New host is {getattr(self.parent.host, 'display_name', str(self.parent.host))}.",
                                    view=self.parent,
                                )
                        else:
                            if self.parent.message:
                                await self.parent.message.edit(
                                    content="Host has left and not enough players remain. Lobby aborted.",
                                    view=None,
                                )
                            self.parent.players.clear()
                            self.parent.host = None

                    # Remove restart button if all players or just the host have left
                    if (not self.parent.players) or (
                        self.parent.host not in self.parent.players
                    ):
                        if (
                            hasattr(self.parent, "restart_message")
                            and self.parent.restart_message
                        ):
                            try:
                                await self.parent.restart_message.edit(
                                    content="Host has left the game. Restarting is no longer available.",
                                    view=None,
                                )
                            except Exception:
                                pass
                        self.parent.restart_message = None

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
                self.abort_button = ui.Button(label="Abort", style=ButtonStyle.danger)
                self.abort_button.callback = self.abort_callback
                self.join_button.callback = self.join_callback
                self.start_button.callback = self.start_callback
                self.add_item(self.abort_button)
                self.add_item(self.join_button)
                self.add_item(self.start_button)
                self.message = None

            async def abort_callback(self, interaction: Interaction):
                if interaction.user != self.host:
                    await interaction.response.send_message(
                        "Only the host can abort the lobby.", ephemeral=True
                    )
                    return
                if self.message:
                    await self.message.edit(content="Lobby aborted.", view=None)  # type: ignore
                await asyncio.sleep(1)  # Give the message time to update
                self.players.clear()
                self.host = None

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
                await self.message.edit(content=f"Players: {', '.join(p.name for p in self.players)}", view=self)  # type: ignore

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
                playerClasses = [
                    (
                        players.Player(player)
                        if not isinstance(player, players.Player)
                        else player
                    )
                    for player in self.players
                ]
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
                    self.last_played_card.affects.remove(
                        0
                    )  # Remove the game itself from affects of this first card
                except ValueError:
                    pass

                # Send initial deck image to all players with leave button
                for player in self.players:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, player
                    )
                    leave_view = self.LeaveView(self, player)
                    player.deck_message = await player.player.send(  # type: ignore
                        file=discord.File(img_bytes, filename="your_deck.png"),
                        view=leave_view,
                    )
                    leave_view.message = player.deck_message  # type: ignore

                gameFinished = False
                while not gameFinished:
                    await asyncio.sleep(
                        2
                    )  # give the players some time to read the last message, in case something happens fast
                    gameFinished = await self.gameTick()

                print(f"{player_names}: Game of infinUno finished.")
                await self.show_restart_button(interaction)
                pygame.quit()

            async def show_restart_button(self, interaction):
                class RestartView(ui.View):
                    def __init__(self, parent):
                        super().__init__(timeout=None)
                        self.parent = parent
                        self.restart_button = ui.Button(
                            label="Restart Game", style=ButtonStyle.success
                        )
                        self.restart_button.callback = self.restart_callback
                        self.add_item(self.restart_button)
                        self.message = None

                    async def restart_callback(self, interaction: Interaction):
                        if interaction.user != self.parent.host:
                            await interaction.response.send_message(
                                "Only the host can restart the game.", ephemeral=True
                            )
                            return
                        elif not any(
                            interaction.user == p.player for p in self.parent.players
                        ):
                            await interaction.response.send_message(
                                "You, the host, are not in the game. Cannot restart. Aborting game.",
                                ephemeral=True,
                            )
                            await self.message.edit(content=f"{self.parent.host} has somehow left the game without losing host status. Game aborted.", view=None)  # type: ignore
                            await asyncio.sleep(1)  # Give the message time to update
                            self.parent.players.clear()
                            self.parent.host = None
                            return
                        await interaction.response.defer()
                        # Restart the game with the same players
                        asyncio.create_task(self.parent.gameStart(interaction))
                        self.stop()
                        await self.message.edit(view=None)  # type: ignore

                view = RestartView(self)
                msg = await interaction.channel.send(
                    f"Game finished! Host can restart the game.", view=view
                )
                view.message = msg
                self.restart_message = msg

            async def gameTick(self):
                self.nextMessageContent = ""
                gameFinished = False
                preventFurtherPlay = False
                current_player = self.players[self.current_player_index]

                # Gather all target players affected by the last played card
                target_players = []
                for offset in self.last_played_card.affects:
                    target_index = (
                        self.current_player_index + offset
                    ) % self.num_players
                    target_players.append(self.players[target_index])

                # Handle stacking draw cards
                if (
                    self.drawCounter != 0
                    or self.last_played_card.add != 0
                    or self.last_played_card.mult != 1.0
                ):
                    if self.drawCounter == 0:
                        if self.last_played_card.add != 0:
                            self.drawCounter = self.last_played_card.add
                            if self.last_played_card.mult != 1.0:
                                self.drawCounter = int(
                                    self.drawCounter * self.last_played_card.mult
                                )
                        elif self.last_played_card.mult != 1.0:
                            self.drawCounter = int(
                                current_player.hand.count() * self.last_played_card.mult
                                - current_player.hand.count()
                            )
                    self.nextMessageContent += (
                        f"\nThere was an existing draw counter of {self.drawCounter}."
                    )
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
                            preventFurtherPlay = True
                            played_card = stackable[0]
                            self.nextMessageContent += f"\n{current_player.name} automatically played their first stackable card: {played_card.name}."
                            target.hand.remove(played_card)
                            self.last_played_card = played_card
                            # Update drawCounter
                            self.drawCounter = int(
                                (self.drawCounter + played_card.add)
                                * played_card.mult  # add first, then multiply for more adding influence when also multiplying
                            )
                            self.nextMessageContent += (
                                f"\nThe draw counter is now {self.drawCounter}."
                            )
                            stackableFound = True
                            break
                    if not stackableFound:
                        for target in target_players:
                            target.hand.draw(self.drawCounter)
                        self.nextMessageContent += f"\n{", ".join([target.name for target in target_players])} drew {self.drawCounter} cards."
                        self.drawCounter = 0  # Reset draw counter

                # Check skip indicator
                if preventFurtherPlay:
                    pass  # we have already played a card, so we cannot play another one
                elif self.last_played_card.skip and current_player in target_players:
                    self.nextMessageContent += (
                        f"\n{current_player.name} could not do anything further."
                    )
                    # we just got skipped. Because this card will also be the last played card for the next player, we must adjust the affects of this card by pushing every value down by one
                    self.last_played_card.affects = [
                        a - 1 for a in self.last_played_card.affects if a - 1 >= 0
                    ]
                    # we remove negative values, because with more players, the probability of this card laying long enough to skip someone from the end of the list decreases enough for us to just not respect you playing it.
                    # DO NOT remove removing negative values, as that will cause the game to get stuck in an infinite loop when there are not more players than affected targets.
                else:
                    # enable the current player to play a card
                    self.nextMessageContent += f"\n{current_player.name} may now play a card. (But for now, the game ends here.)"
                    gameFinished = True  # For now, we end the game as soon as a card can be played by the player

                # Send all players an updated view of their deck together with the messageContent
                for player in self.players:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, player
                    )
                    leave_view = self.LeaveView(self, player)
                    content = f"{self.nextMessageContent}"
                    if hasattr(player, "deck_message") and player.deck_message:
                        # Edit the previous message with new image and content
                        player.deck_message = await player.deck_message.edit(
                            content=content,
                            attachments=[
                                discord.File(img_bytes, filename="your_deck.png")
                            ],
                            view=leave_view,
                        )  # type: ignore
                        leave_view.message = player.deck_message
                    else:
                        # Send a new message if none exists
                        msg = await player.player.send(  # type: ignore
                            content=f"This is your deck. {content}",
                            file=discord.File(img_bytes, filename="your_deck.png"),
                            view=leave_view,
                        )
                        player.deck_message = msg
                        leave_view.message = msg

                # Update current player index for the next turn
                self.current_player_index = (
                    self.current_player_index + 1
                ) % self.num_players
                return gameFinished

        view = JoinView(ctx.user)
        await ctx.response.send_message(
            "Press **Join/Leave** to participate in InfinUno. The host can press **Start** when ready.",
            view=view,
        )
        view.message = await ctx.original_response()
