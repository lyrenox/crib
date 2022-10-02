import discord
from discord import Embed
from database import UserEntry

class Leaderboard():
    def __init__(self, guild: int, guild_name: str, guild_icon: str, user: int = None):
        self.guild = guild
        self.guild_name = guild_name
        self.guild_icon = guild_icon
        self.user = user
        self.scope = 10

    def get_page_from_user(self):
        data = UserEntry(str(self.guild))
        sorted = data.sort()
        
        if self.user != None:
            try:
                result = [item for item in sorted if item['user_id'] == self.user][0]
                return ((sorted.index(result) + 1) // self.scope) + 1
            except:
                print(f"Cannot find user {self.user} in leaderboard")
                return 1
        else:
            return 1

    def get_max_page(self):
        data = UserEntry(str(self.guild))
        sorted = data.sort()
        return len(sorted) // self.scope + 1

    def create_embed(self, page: int):
        data = UserEntry(str(self.guild))
        sorted = data.sort()

        start = (page-1) * self.scope + 1
        end = min([(page * self.scope), len(sorted)])
        viewport = sorted[start-1:end]
        i = 0
        list = ""
        for item in viewport:
            if start + i == 1:
                badge = "🥇"
            elif start + i == 2:
                badge = "🥈"
            elif start + i == 3:
                badge = "🥉"
            else:
                badge = "👏"
            list += f"{badge}`{start+i}` <@!{item['user_id']}> ⏣ {item['amount']:,}\n"
            i += 1
        embed = Embed(title="Top Donators", description=list)
        embed.set_footer(text=f"Showing {start} to {end} out of {len(sorted)} • {self.guild_name}", icon_url=self.guild_icon)
        return embed

class Paginator(discord.ui.View):
    def __init__(self, guild: int, guild_name: str, guild_icon: str, page: int):
        super().__init__()
        self.page = page
        self.params = [guild, guild_name, guild_icon]
        self.leaderboard = Leaderboard(*self.params)
        
    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary, custom_id="first")
    async def first(self, button, interaction):
        self.page = 1
        newEmbed = self.leaderboard.create_embed(self.page)
        await interaction.response.edit_message(embed=newEmbed, view=Paginator(*self.params, self.page))

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary, custom_id="prev")
    async def prev(self, button, interaction):
        self.page -= 1
        newEmbed = self.leaderboard.create_embed(self.page)
        await interaction.response.edit_message(embed=newEmbed, view=Paginator(*self.params, self.page))

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary, custom_id="next")
    async def next(self, button, interaction):
        self.page += 1
        newEmbed = self.leaderboard.create_embed(self.page)
        await interaction.response.edit_message(embed=newEmbed, view=Paginator(*self.params, self.page))

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary, custom_id="last")
    async def last(self, button, interaction):
        self.page = self.leaderboard.get_max_page()
        newEmbed = self.leaderboard.create_embed(self.page)
        await interaction.response.edit_message(embed=newEmbed, view=Paginator(*self.params, self.page))


         