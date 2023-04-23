import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import random
from collections import OrderedDict
from operator import getitem


class SnowballFight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cred_obj = firebase_admin.credentials.Certificate('discord-snowball-fight-bot-firebase-adminsdk-j79ek-bb8199c11e.json')
        self.default_app = firebase_admin.initialize_app(cred_obj, {
            'databaseURL': 'https://discord-snowball-fight-bot-default-rtdb.firebaseio.com/'
        })
        self.ref = db.reference("/")

    def register_user_if_not_already(self, user_id, guild_id):
        # add guild if not already there
        if self.ref.child(guild_id + user_id).get() is None:
            self.ref.update({
                guild_id + user_id: {
                    "hits": 0,
                    "was_hit": 0,
                    "snowballs": 0,
                    "total_snowballs": 0,
                    "misses": 0
                }
            })

    @commands.command()
    async def stats(self, ctx):
        thrower_id = str(ctx.message.author.id)
        guild_id = str(ctx.guild.id)
        self.register_user_if_not_already(thrower_id, guild_id)

        current_hits = self.ref.child(guild_id+thrower_id).get()["hits"]
        current_snowballs = self.ref.child(guild_id+thrower_id).get()["total_snowballs"]
        current_misses = self.ref.child(guild_id+thrower_id).get()["misses"]
        await ctx.send(embed=discord.Embed(description="**" + str(ctx.message.author.name) +
                       ": Here is your personal statistics!**\n"
                       "```Successful throws:   " + str(current_hits) + "\n"
                       "Unsuccessful throws: " + str(current_misses) + "\n"
                       "Snowballs collected: " + str(current_snowballs) + "\n"
                       "\n```", color=0xcc3813))

    @commands.command()
    async def collect(self, ctx):
        thrower_id = str(ctx.message.author.id)
        guild_id = str(ctx.guild.id)
        self.register_user_if_not_already(thrower_id, guild_id)

        # update snowball count
        current_snowballs = db.reference("/" + guild_id + thrower_id).get()["snowballs"]
        current_total = db.reference("/" + guild_id + thrower_id).get()["total_snowballs"]
        if current_snowballs < 5:
            self.ref.child(guild_id + thrower_id).update({
                "snowballs": current_snowballs + 1,
                "total_snowballs": current_total + 1
            })
            if current_snowballs == 0:
                await ctx.send(embed=discord.Embed(description="**" + str(ctx.message.author.name) + "** has collected a snowball, preparing for war! (•̀ω•́)", color=0xcc3813))
            else:
                await ctx.send(embed=discord.Embed(description="**" + str(ctx.message.author.name) + "** has collected another snowball, they now have "
                               + str(current_snowballs + 1) + " snowballs! (^o^)", color=0xcc3813))
        else:
            await ctx.send(embed=discord.Embed(description="**" +
                str(ctx.message.author.name) + "** has maxed out on the amount of snowballs you can carry! (•́o•̀)", color=0xcc3813))

    @commands.command()
    async def throw(self, ctx, user: discord.Member):
        '''if ctx.message.author.id == user.id:
            await ctx.send(embed=discord.Embed(description="You can't throw a snowball at yourself!", color=0xcc3813))
            return'''

        thrower_id = str(ctx.message.author.id)
        thrower_name = str(ctx.message.author.name)
        guild_id = str(ctx.guild.id)
        self.register_user_if_not_already(thrower_id, guild_id)
        self.register_user_if_not_already(str(user.id), guild_id)

        coin_flip = random.random()

        # update thrower's hits count
        if self.ref.child(guild_id+thrower_id).get()["snowballs"] > 0:
            # snowballs
            current_snowballs = db.reference("/" + guild_id + thrower_id).get()["snowballs"] - 1
            self.ref.child(guild_id+thrower_id).update({"snowballs": current_snowballs})

            if coin_flip > 0.5:
                if ctx.message.author.id == user.id:
                    await ctx.send(embed=discord.Embed(
                        description="**" + thrower_name + "** threw a snowball into the air and it landed next to them! (^_^)", color=0xcc3813))
                else:
                    await ctx.send(embed=discord.Embed(description="**" + thrower_name + "** threw a snowball at **" + str(user.name) + "** and missed, better luck next time! (ゝω・)", color=0xcc3813))
                    # update miss count
                    current_score = db.reference("/" + guild_id + thrower_id).get()["misses"] + 1
                    self.ref.child(guild_id+thrower_id).update({"misses": current_score})
            else:
                if ctx.message.author.id == user.id:
                    await ctx.send(embed=discord.Embed(
                        description="**" + thrower_name + "** threw a snowball into the air and it landed on their face! (^_^メ)",
                        color=0xcc3813))
                else:
                    await ctx.send(embed=discord.Embed(description="**" + thrower_name + "** threw a snowball at **" + str(user.name) + "** and hit them in their face! (*>ω<)", color=0xcc3813))
                    # update hit count
                    current_score = db.reference("/" + guild_id + thrower_id).get()["hits"] + 1
                    self.ref.child(guild_id+thrower_id).update({"hits": current_score})

                    # update victim's been-hit count
                    current_score = db.reference("/" + guild_id + str(user.id)).get()["was_hit"] + 1
                    self.ref.child(guild_id+str(user.id)).update({"was_hit": current_score})
        else:
            await ctx.send(embed=discord.Embed(description="**" + thrower_name + "** has ran out of snowballs, use \"s!collect\" to collect more! (＾ω＾)", color=0xcc3813))

    @commands.command()
    async def leaderboard(self, ctx):
        guild_id = str(ctx.guild.id)

        hits_query = self.ref.order_by_key().start_at(guild_id).end_at(guild_id + '\uf8ff')
        sorted_hits = OrderedDict(reversed(sorted(hits_query.get().items(), key=lambda x: getitem(x[1], 'hits'))))

        idx = 1
        out_string = "**Players who have the most successful throws:**\n```"
        for key, value in sorted_hits.items():
            username = await self.bot.fetch_user(key[len(guild_id):])
            out_string += "#" + str(idx) + ": " + username.name + "\n"
            idx += 1
            if idx == 10:
                break

        idx = 1
        out_string += "```\n**Players who have been subjected to the most hits:**\n```"

        hurts_query = self.ref.order_by_key().start_at(guild_id).end_at(guild_id + '\uf8ff')
        sorted_hurts = OrderedDict(reversed(sorted(hurts_query.get().items(), key=lambda x: getitem(x[1], 'was_hit'))))
        for key, value in sorted_hurts.items():
            username = await self.bot.fetch_user(key[len(guild_id):])
            out_string += "#" + str(idx) + ": " + username.name + "\n"
            idx += 1
            if idx == 10:
                break

        await ctx.send(embed=discord.Embed(description=out_string + "```", color=0xcc3813))


async def setup(bot):
    await bot.add_cog(SnowballFight(bot))

