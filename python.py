import os
import re
import aiohttp
from collections import defaultdict

import discord
import peony
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from discord.ext import commands

PATH = os.path.join("data", "DanFarias2000")
JSON = os.path.join(PATH, "settings.json")
ROLES = ['Member', 'Guest']


def nested_dict():
    """Recursively nested defaultdict."""
    return defaultdict(nested_dict)


class DanFarias2000:
    """DanFarias2000 Twitter client.
    User type !IslaTweet message which gets broadcasted to @DanFarias2000
    """

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.settings = nested_dict()
        self.settings.update(dataIO.load_json(JSON))

        if self.settings.get("twitter_api") is None:
            self.settings["twitter_api"] = {
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }
            dataIO.save_json(JSON, self.settings)


    def peony_client(self, **kwargs):
        """Return Twitter API instance."""
        return peony.PeonyClient(**self.settings['twitter_api'], **kwargs)

    @commands.group(pass_context=True)
    async def DanFarias2000set(self, ctx):
        """Settings."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @checks.is_owner()
    @DanFarias2000set.command(name="twitterapi", pass_context=True)
    async def DanFarias2000set_twitterapi(self,
                                       ctx, consumer_key=None, consumer_secret=None,
                                       access_token=None, access_token_secret=None):
        """Twitter API settings"""
        if not any([consumer_key, consumer_secret, access_token, access_token_secret]):
            await self.bot.send_cmd_help(ctx)
            em = discord.Embed(title="DanFarias2000 Settings")
            for k, v in self.settings['twitter_api'].items():
                em.add_field(name=k, value=v)
            await self.bot.send_message(ctx.message.author, embed=em)
            return

        self.settings.update({
            "twitter_api": {
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }
        })
        dataIO.save_json(JSON, self.settings)
        await self.bot.say("Settings updated")
        await self.bot.delete_message(ctx.message)

    @commands.has_any_role(*ROLES)
    @commands.command(aliases=['rrant'], pass_context=True, no_pm=True)
    async def DanFarias2000(self, ctx, *, msg):
        """Post a Tweet from @DanFarias2000."""
        with aiohttp.ClientSession() as session:
            client = self.peony_client(sessions=session)
            author = ctx.message.author
            author_initials = "".join(re.findall("[a-zA-Z0-9]+", author.display_name))[:2]

            attachment_urls = [attachment['url'] for attachment in ctx.message.attachments]

            try:
                media_ids = []
                if len(attachment_urls):
                    for url in attachment_urls:
                        media = await client.upload_media(url, chunk_size=2**18, chunked=True)
                        media_ids.append(media.media_id)

                tweet = "[{}] {}".format(author_initials, msg)
                resp = await client.api.statuses.update.post(status=tweet, media_ids=media_ids)
            except peony.exceptions.PeonyException as e:
                await self.bot.say("Error tweeting: {}".format(e.response))
                return

            url = "https://twitter.com/{0[user][screen_name]}/status/{0[id_str]}".format(resp)
            await self.bot.say("Tweeted: <{}>".format(url))

    @commands.has_any_role(*ROLES)
    @commands.command(aliases=['rrantrt'], pass_context=True, no_pm=True)
    async def DanFarias2000_retweet(self, ctx, arg):
        """Retweet by original tweet URL or status ID."""
        client = self.peony_client()
        status_id = arg
        if arg.startswith('http'):
            status_id = re.findall("[0-9]+$", arg)[0]
        try:
            resp = await client.api.statuses.retweet.post(id=status_id)
        except peony.exceptions.PeonyException as e:
            await self.bot.say("Error tweeting: {}".format(e.response))
            return

        url = "https://twitter.com/{0[user][screen_name]}/status/{0[id_str]}".format(resp)
        await self.bot.say("Tweeted: <{}>".format(url))



def check_folder():
    """Check folder."""
    os.makedirs(PATH, exist_ok=True)


def check_file():
    """Check files."""
    if not dataIO.is_valid_json(JSON):
        dataIO.save_json(JSON, {})


def setup(bot):
    """Setup."""
    check_folder()
    check_file()
    n = DanFarias2000(bot)
    bot.add_cog(n)
