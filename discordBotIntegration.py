from . import main
import discord
from discord import ui, Interaction, ButtonStyle

def init(bot):
    @bot.tree.command(name='infinuno')
    async def infinUno(ctx):
        """Starts the InfinUno game."""
        class JoinView(ui.View):
            def __init__(self, host):
                super().__init__(timeout=None)
                self.players = set()
                self.host = host
                self.join_button = ui.Button(label="Join/Leave", style=ButtonStyle.primary)
                self.start_button = ui.Button(label="Start", style=ButtonStyle.success, disabled=True)
                self.join_button.callback = self.join_callback
                self.start_button.callback = self.start_callback
                self.add_item(self.join_button)
                self.add_item(self.start_button)
                self.message = None

            async def join_callback(self, interaction: Interaction):
                user = interaction.user
                if user in self.players:
                    self.players.remove(user)
                    await interaction.response.send_message("You left the game.", ephemeral=True)
                else:
                    self.players.add(user)
                    await interaction.response.send_message("You joined the game.", ephemeral=True)
                self.start_button.disabled = len(self.players) == 0 or self.host not in self.players
                await self.message.edit(view=self) # type: ignore

            async def start_callback(self, interaction: Interaction):
                if interaction.user != self.host:
                    await interaction.response.send_message("Only the host can start the game.", ephemeral=True)
                    return
                if len(self.players) == 0:
                    await interaction.response.send_message("No players have joined.", ephemeral=True)
                    return
                await interaction.response.send_message("Game started! Check your DMs.", ephemeral=True)
                for player in self.players:
                    try:
                        await player.send("The InfinUno game is starting!")
                    except Exception:
                        pass
                self.stop()
                await self.message.edit(view=None) # type: ignore

        view = JoinView(ctx.user)
        await ctx.response.send_message(
            "Press **Join/Leave** to participate in InfinUno. The host can press **Start** when ready.",
            view=view
        )
        view.message = await ctx.original_response()
