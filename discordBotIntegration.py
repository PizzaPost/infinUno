import random
from . import main, cards, players, visuals
import discord
from discord import ui, Interaction, ButtonStyle
import asyncio
import pygame
import io
from PIL import Image


def renderGameStateBytes(window, last_played_card, player, Players):
    deck_image = visuals.renderGameState(window, last_played_card, player, Players)
    # Convert pygame surface to string buffer
    data = pygame.image.tostring(deck_image, "RGBA")
    size = deck_image.get_size()
    # Create PIL Image
    image = Image.frombytes("RGBA", size, data)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


def init(bot, tree=None):
    if not tree:
        tree = bot.tree
    @tree.command(name="infinunodeck")
    async def infinUnoRandomDeckPreview(ctx):
        """Generates a random deck and sends it as an image."""
        last_played_card = cards.randomCard()
        window = visuals.Window(
            "InfinUno Deck Preview", pygame.display.set_mode((800, 600), pygame.HIDDEN)
        )
        img_bytes = renderGameStateBytes(
            window, last_played_card, players.Player(), [players.Player()]
        )
        await ctx.response.send_message(file=discord.File(img_bytes, filename="your_deck.png"))

    @tree.command(name="infinuno")
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
                for player in self.players:
                    player.hand.clear()
                    player.hand.draw(7)
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
                self.last_played_card = cards.randomCard()
                self.nextMessageContent = ""
                self.current_player_index = -1
                self.num_players = len(self.players)
                self.drawCounter = 0

                try:
                    self.last_played_card.affects.remove(
                        0
                    )  # Remove the game itself from affects of this first card
                except ValueError:
                    pass

                for player in self.players:
                    await player.player.send("I will send your deck here in a few seconds.")  # type: ignore

                await asyncio.sleep(5)

                # Send initial deck image to all players with leave button
                for player in self.players:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, player, self.players
                    )
                    leave_view = self.LeaveView(self, player)
                    player.deck_message = await player.player.send(  # type: ignore
                        file=discord.File(img_bytes, filename="your_deck.png"),
                        view=leave_view,
                    )
                    leave_view.message = player.deck_message  # type: ignore

                gameFinished = False
                while not gameFinished and self.players:
                    await asyncio.sleep(1)
                    # give the players some time to read the last message, in case something happens fast
                    gameFinished = await self.gameTick()
                    await asyncio.sleep(1)

                print(f"{player_names}: Game of infinUno finished.")
                await self.show_restart_button(interaction)

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
                mayPlay = False
                if not self.players:
                    return True

                class CardSelect(ui.Select):
                    def __init__(self, cards):
                        options = [
                            discord.SelectOption(
                                label=c.name,
                                description=str(c),
                                value=str(i),
                            )
                            for i, c in enumerate(cards)
                        ]
                        super().__init__(
                            placeholder="Choose a card to play",
                            min_values=1,
                            max_values=1,
                            options=options,
                        )
                        self.cards = cards
                        self.selected_card = None

                    async def callback(self, interaction: Interaction):
                        idx = int(self.values[0])
                        self.selected_card = self.cards[idx]
                        self.view.stop()  # type: ignore
                        await interaction.response.defer()

                class CardView(ui.View):
                    def __init__(self, cards):
                        super().__init__(timeout=None)
                        # Limit to 25 unique cards by name
                        seen = set()
                        unique_cards = []
                        for c in cards:
                            if c.name not in seen:
                                seen.add(c.name)
                                unique_cards.append(c)
                        if len(unique_cards) > 25:
                            limitedCards = random.sample(unique_cards, 25)
                        else:
                            limitedCards = unique_cards
                        self.select = CardSelect(limitedCards)
                        self.add_item(self.select)

                # Gather all target players affected by the last played card
                self.num_players = len(self.players)
                target_players = []
                for offset in self.last_played_card.affects:  # type: ignore
                    target_index = (
                        self.current_player_index + offset
                    ) % self.num_players
                    if target_index >= 0:
                        target_players.append(self.players[target_index])
                self.current_player_index = (
                    self.current_player_index + 1
                ) % self.num_players
                current_player = self.players[self.current_player_index]

                # Handle stacking draw cards
                if (
                    self.drawCounter != 0
                    or self.last_played_card.add != 0
                    or self.last_played_card.mult != 1.0
                    or self.last_played_card.pow != 1.0
                ):
                    if self.drawCounter == 0:
                        if self.last_played_card.add != 0:  # type: ignore
                            self.drawCounter = self.last_played_card.add  # type: ignore
                            self.last_played_card.add = 0  # type: ignore # Remove the add from the card
                            if self.last_played_card.mult != 1.0:  # type: ignore
                                self.drawCounter = int(
                                    self.drawCounter * self.last_played_card.mult  # type: ignore
                                )
                                self.last_played_card.mult = 1.0  # type: ignore # Reset multiplier after applying
                            if self.last_played_card.pow != 1.0:  # type: ignore
                                self.drawCounter = int(
                                    self.drawCounter**self.last_played_card.pow  # type: ignore
                                )
                                self.last_played_card.pow = 1.0  # type: ignore # Reset power after applying
                        elif self.last_played_card.mult != 1.0:  # type: ignore
                            self.drawCounter = int(
                                current_player.hand.count() * self.last_played_card.mult  # type: ignore
                                - current_player.hand.count()
                            )
                            self.last_played_card.mult = 1.0  # type: ignore # Reset multiplier after applying
                            if self.last_played_card.pow != 1.0:  # type: ignore
                                self.drawCounter = int(
                                    self.drawCounter**self.last_played_card.pow  # type: ignore
                                )
                                self.last_played_card.pow = 1.0  # type: ignore # Reset power after applying
                        elif self.last_played_card.pow != 1.0:  # type: ignore
                            self.drawCounter = int(
                                current_player.hand.count() ** self.last_played_card.pow  # type: ignore
                                - current_player.hand.count()
                            )
                            self.last_played_card.pow = 1.0  # type: ignore # Reset power after applying
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
                            # Ask the user to pick a stackable card from a dropdown
                            stackable_view = CardView(stackable)

                            self.nextMessageContent += f"\n{target.name} has stackable cards and should pick one."
                            target.deck_message = await target.deck_message.edit(
                                content=f"{self.nextMessageContent}",
                                attachments=[
                                    discord.File(
                                        renderGameStateBytes(
                                            self.window,
                                            self.last_played_card,
                                            target,
                                            self.players,
                                        ),
                                        filename="your_deck.png",
                                    )
                                ],
                                view=stackable_view,
                            )
                            await stackable_view.wait()
                            played_card = stackable_view.select.selected_card
                            self.nextMessageContent += f"\n{target.name} picked: {played_card.name}."  # type: ignore
                            target.deck_message = await target.deck_message.edit(content=f"{self.nextMessageContent}", view=None)  # type: ignore
                            if played_card is None:
                                # If user didn't pick, just pick the first one as fallback
                                played_card = stackable[0]
                            preventFurtherPlay = True
                            self.playCard(played_card, current_player, target)
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
                elif self.last_played_card.skip and current_player in target_players:  # type: ignore
                    self.nextMessageContent += (
                        f"\n{current_player.name} could not do anything further."
                    )
                    # we just got skipped. Because this card will also be the last played card for the next player, we must adjust the affects of this card by pushing every value down by one
                    self.last_played_card.affects = [  # type: ignore
                        a - 1 for a in self.last_played_card.affects if a - 1 >= 0  # type: ignore
                    ]
                    # we remove negative values, because with more players, the probability of this card laying long enough to skip someone from the end of the list decreases enough for us to just not respect you playing it.
                    # DO NOT remove removing negative values, as that will cause the game to get stuck in an infinite loop when there are not more players than affected targets.
                else:
                    self.nextMessageContent += (
                        f"\n{current_player.name} may now play a card."
                    )
                    playableCards = [
                        c
                        for c in current_player.hand.cards
                        if c.color in self.last_played_card.nextColor
                        or "choice" in self.last_played_card.nextColor
                        or (c.corner == self.last_played_card.corner and c.corner != "")
                        or c.color == "choice"
                    ]

                    if not playableCards:
                        i = 0
                        cardPick = cards.Card("emptyCard")
                        while cardPick.color not in self.last_played_card.nextColor and cardPick.color != "choice" and (cardPick.corner != self.last_played_card.corner or cardPick.corner == ""):  # type: ignore
                            # Pick a random card until we find one that matches the last played card's nextColor
                            cardPick = cards.randomCard()
                            current_player.hand.add(cardPick)
                            i += 1
                            if current_player not in self.players:
                                # If the player has left the game, stop this gameTick.
                                return False
                        self.nextMessageContent += f"\n{current_player.name} had no playable cards and drew {i} cards from the deck."  # type: ignore
                        playableCards = [cardPick]

                    cardView = CardView(playableCards)  # type: ignore
                    current_player.deck_message = await current_player.deck_message.edit(  # type: ignore
                        content=f"{self.nextMessageContent}",
                        attachments=[
                            discord.File(
                                renderGameStateBytes(
                                    self.window,
                                    self.last_played_card,
                                    current_player,
                                    self.players,
                                ),
                                filename="your_deck.png",
                            )
                        ],
                        view=cardView,  # type: ignore
                    )
                    await cardView.wait()
                    self.playCard(
                        cardView.select.selected_card, current_player, current_player
                    )
                    self.nextMessageContent += f"\n{current_player.name} played: {cardView.select.selected_card.name}."  # type: ignore

                # Send all players an updated view of their deck together with the messageContent
                for player in self.players:
                    img_bytes = renderGameStateBytes(
                        self.window, self.last_played_card, player, self.players
                    )
                    leave_view = self.LeaveView(self, player)
                    content = f"{self.nextMessageContent}"
                    # Edit the previous message with new image and content
                    player.deck_message = await player.deck_message.edit(  # type: ignore
                        content=content,
                        attachments=[discord.File(img_bytes, filename="your_deck.png")],
                        view=leave_view,
                    )  # type: ignore
                    leave_view.message = player.deck_message

                if current_player.hand.count() == 0:
                    gameFinished = True
                    self.nextMessageContent += (
                        f"\n{current_player.name} has won the game!"
                    )
                    await current_player.player.send(  # type: ignore
                        f"Congratulations {current_player.name}, you have won the game of InfinUno!"
                    )

                return gameFinished

            def playCard(self, played_card, current_player, target):
                """
                Called when a player plays a card.

                Removes the played card from the target player's hand and sets it as the last played card.
                If the played card has the reverse attribute set to True, reverses the order of play and adjusts the current player index accordingly.

                :param played_card: The card played by the current player.
                :param current_player: The current player.
                :param target: The target player.
                """
                target.hand.remove(played_card)
                self.last_played_card = played_card
                if self.drawCounter != 0:
                    self.drawCounter = int(
                        (self.drawCounter + played_card.add) * played_card.mult  # type: ignore
                    )
                    # remove used up effects from the played card
                    played_card.add = 0
                    played_card.mult = 1.0
                if played_card.reverse:
                    self.players.reverse()
                    self.current_player_index = self.players.index(current_player)

        view = JoinView(ctx.user)
        await ctx.response.send_message(
            "Press **Join/Leave** to participate in InfinUno. The host can press **Start** when ready.",
            view=view,
        )
        view.message = await ctx.original_response()
