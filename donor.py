from email.policy import default
import discord
from discord import option, Embed, SlashCommandGroup
from discord.ext import commands

from database import UserEntry
from leaderboard import Leaderboard, Paginator

class Donor(commands.Cog):
    dono = SlashCommandGroup("dono", default_member_permissions=discord.Permissions(manage_guild=True))

    def __init__(self,bot):
        self.bot = bot

    @discord.user_command(name="View Profile")
    async def view_profile(self, ctx, user: discord.Member):
        try:
            donor = UserEntry(str(ctx.guild.id), user.id)
            amount = donor.fetch()['amount']
            donations = donor.fetch()['donations']

            sorted = donor.sort()
            try:
                result = [item for item in sorted if item['user_id'] == user.id][0]
                rank = sorted.index(result) + 1
            except:
                print(f"Cannot find user {self.user} in leaderboard")
                rank = "NaN"

        except Exception as e:
            print(f"Unable to view data for user {user.id}: {e}")
            new_embed = Embed(description="That user hasn't donated, or maybe something got corrupted lol")

        else:
            new_embed = Embed(title=f"{user.name}'s donations", description=f"<@!{user.id}> (Rank {rank})")
            new_embed.add_field(name="Amount Donated", value=f"`{amount:,}`", inline=False)
            new_embed.add_field(name="Times Donated (very inaccurate)", value=f"`{donations}`", inline=False)
            new_embed.set_thumbnail(url=user.display_avatar.url)
            new_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)

        await ctx.respond(embed=new_embed)

    @discord.slash_command(name="profile", description="View your donations")
    @option('user', description="View someone else's donations.", required=False, default=None)
    async def profile(self, ctx, user:discord.Member):
        if user is None:
            user = ctx.author

        try:
            donor = UserEntry(str(ctx.guild.id), user.id)
            amount = donor.fetch()['amount']
            donations = donor.fetch()['donations']

            sorted = donor.sort()
            try:
                result = [item for item in sorted if item['user_id'] == user.id][0]
                rank = sorted.index(result) + 1
            except:
                print(f"Cannot find user {self.user} in leaderboard")
                rank = "NaN"

        except Exception as e:
            print(f"Unable to view data for user {user.id}: {e}")
            new_embed = Embed(description="That user hasn't donated, or maybe something got corrupted lol")

        else:
            new_embed = Embed(title=f"{user.name}'s donations", description=f"<@!{user.id}> (Rank {rank})")
            new_embed.add_field(name="Amount Donated", value=f"`{amount:,}`", inline=False)
            new_embed.add_field(name="Times Donated (very inaccurate)", value=f"`{donations}`", inline=False)
            new_embed.set_thumbnail(url=user.display_avatar.url)
            new_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)

        await ctx.respond(embed=new_embed)

    @dono.command(name="add", description="Add to your donations.")
    @option('amount', description="The amount to add", min_value=1)
    @option('user', description="Add to someone else's donations.", required=False, default=None)
    async def add(self, ctx, amount: int, user: discord.Member):
        if user is None:
            user = ctx.author

        donor = UserEntry(str(ctx.guild.id), user.id)
        try:
            if donor.fetch() is None:
                old_amount = donor.fetch()['amount']
            else:
                old_amount = 0
            donor.update_amount(amount)
            new_embed = Embed(description=f"Successfully added {amount:,} to {user.mention}'s donations.\nTotal: `{old_amount:,}` → `{donor.fetch()['amount']:,}`")
        except Exception as e:
            print(f"Unable to update data for user {user.id}: {e}")
            new_embed = Embed(description="Something went wrong while updating donations.")

        await ctx.respond(embed=new_embed)

    @dono.command(name="remove", description="Remove from your donations.")
    @option('amount', description="The amount to remove", min_value=1)
    @option('user', description="Remove from someone else's donations.", required=False, default=None)
    async def remove(self, ctx, amount: int, user: discord.Member):
        if user is None:
            user = ctx.author

        donor = UserEntry(str(ctx.guild.id), user.id)
        if donor.fetch() is None:
            new_embed = Embed(description="Dude, that guy hasn't even donated yet.")
        else:
            if donor.fetch()['amount'] < amount:
                amount = donor.fetch()['amount']
            try:
                if donor.fetch() is None:
                    old_amount = donor.fetch()['amount']
                else:
                    old_amount = 0
                donor.update_amount(amount * -1)
                new_embed = Embed(description=f"Successfully removed {amount:,} from {user.mention}'s donations.\nTotal: `{old_amount:,}` → `{donor.fetch()['amount']:,}`")
            except Exception as e:
                print(f"Unable to update data for user {user.id}: {e}")
                new_embed = Embed(description="Something went wrong while updating donations.")

        await ctx.respond(embed=new_embed)
    
    @discord.slash_command(name="leaderboard", description="Check who's on top!")
    @option('page', description="Go to page", required=False, min_value=1, default=1)
    @option('jump_to', description="Find a user's rank in this leaderboard.", required=False)
    async def leaderboard(self, ctx, page: int, jump_to: discord.Member):
        if jump_to is None:
            leaderboard = Leaderboard(ctx.guild.id, ctx.guild.name, ctx.guild.icon.url)
            newEmbed = leaderboard.create_embed(page)
        else:
            leaderboard = Leaderboard(ctx.guild.id, ctx.guild.name, ctx.guild.icon.url, jump_to.id)
            page = leaderboard.get_page_from_user()
            newEmbed = leaderboard.create_embed(page)
        view = Paginator(ctx.guild.id, ctx.guild.name, ctx.guild.icon.url, page)
        await ctx.respond(embed=newEmbed, view=view)


def setup(bot):
    bot.add_cog(Donor(bot))
    