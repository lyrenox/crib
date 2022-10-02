import re
from typing import Union

import discord
from discord import option, Embed
from discord.ext import commands
from pycord.multicog import add_to_group

from database import UserEntry


class Transfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @add_to_group("dono")    
    @discord.slash_command(name="transfer", description="Transfer donations (Noumenon only) through a text file")
    @option('file', description="The file to read.")
    async def transfer(self, ctx, file:discord.Attachment):
        if not file.filename.endswith('.txt'):
            await ctx.respond("Please provide a `.txt` file!", ephemeral=True)
        else:
            file = await file.to_file()
            content = file.fp.read()
            content = content.decode('utf-8')

            def search(string:str): # Returns a list of users with their respective data.
                lines = list(string.split('\r\n'))
                members = [m for m in ctx.guild.members if not m.bot]
                
                for line in lines:
                    data = re.split(r'\s{2,}', line)

                    if len (data) == 3:

                        if ',' in data[1]:
                            data[1] = data[1].replace(',', '')

                            for arg in data:
                                if arg.isnumeric():
                                    data[data.index(arg)] = int(arg)
                            
                            if isinstance(data[0], Union[str, int]) and isinstance(data[1], int) and isinstance(data[2], int):
                                if not isinstance(data[0], int): # The user part is not represented by an ID.
                                    if data[0].endswith('...'):
                                        member = discord.utils.find(lambda m: (m.name + '#' + m.discriminator).startswith(data[0].removesuffix('...')), members)
                                        data[0] = None if member is None else member.id
                                    else:
                                        splitted = data[0].rsplit('#', 1)
                                        member = discord.utils.get(members, name=splitted[0], discriminator=splitted[1])
                                        data[0] = None if member is None else member.id
                            
                            if data[0] is not None:
                                yield data

            returned = search(content)
            await ctx.respond(f"Transfer Started.", ephemeral=True)

            processed = await ctx.send("Transferring...")
            i = 0
            passed = 0
            failed = 0
            for item in returned:
                i += 1
                try:
                    donor = UserEntry(str(ctx.guild.id), item[0])
                    donor.set_amount(item[1])
                except Exception as e:
                    failed += 1
                    print(f"Failed to transfer user {item[0]}: {e}")
                else:
                    passed += 1
            await processed.edit(content=f"Successfully transferred {i} users.", embed=Embed(description=f"`{passed}` successful\n`{failed}` failed"))


def setup(bot):
    bot.add_cog(Transfer(bot))