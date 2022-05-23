from discord import Interaction
from discord.ui import View, Button, button
from discord.components import ButtonStyle


class Search(View):
    def __init__(self, embeds, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current = 0
        self.embeds = embeds

        # 0 row
        self.back = Button(emoji='◀', row=0)
        self.page = Button(label=f'Page {self.current + 1}/{len(self.embeds)}', disabled=True, row=0)
        self.fwd = Button(emoji='▶', row=0)

        self.add_item(self.back)
        self.add_item(self.page)
        self.add_item(self.fwd)

        # 1 row
        self.add_item(Button(label=' ', disabled=True, row=1))
        self.lock = Button(label='Add this', style=ButtonStyle.green, row=1)
        self.add_item(self.lock)
        self.add_item(Button(label=' ', disabled=True, row=1))

        self.back.callback = self.back_callback
        self.fwd.callback = self.fwd_callback
        self.lock.callback = self.lock_callback

    async def followup_callback(self, interaction):
        if self.current == len(self.embeds):
                self.current = 0
        elif self.current < 0:
            self.current = len(self.embeds) - 1

        self.page.label = f'Page {self.current + 1}/{len(self.embeds)}'
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    async def back_callback(self, interaction: Interaction):
        self.current -= 1
        await self.followup_callback(interaction)
        
    async def fwd_callback(self, interaction: Interaction):
        self.current += 1
        await self.followup_callback(interaction)
    
    async def lock_callback(self, interaction: Interaction):
        self.stop()


class Playlist(View):
    def __init__(self, cog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cog = cog

    def disable_all(self):
        self.rename.disabled = True
        self.load.disabled = True
        self.delete.disabled = True

    @button(label='Rename')
    async def rename(self, interaction: Interaction, button: Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        self.returned_callback = self.cog.rename_playlist
        self.stop()
    
    @button(label='Load', style=ButtonStyle.green)
    async def load(self, interaction: Interaction, button: Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        self.returned_callback = self.cog.load_playlist
        self.stop()

    @button(label='Delete', style=ButtonStyle.red)
    async def delete(self, interaction: Interaction, button: Button):
        await interaction.response.edit_message(view=self)
        self.returned_callback = self.cog.delete_playlist
        self.stop()

    async def on_timeout(self):
        self.disable_all()
