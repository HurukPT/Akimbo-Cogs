import discord
import string
from tabulate import tabulate

from redbot.core import Config
from redbot.core import commands
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify

from .utils import *


class Spellbook(commands.Cog):
    """A D&D 5e Cog for Wizards to manage their spellbooks"""

    def __init__(self, bot):
        self.bot = bot
        default_member = {
            "Spell": []
        }
        default_guild = {
            "db": []
        }
        self.config = Config.get_conf(self, identifier=42)
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)

    @commands.command(name="signup")
    @commands.guild_only()
    async def _reg(self, ctx):
        """Sign up to get your own spellbook!"""

        server = ctx.guild
        user = ctx.author
        db = await self.config.guild(server).db()
        if user.id not in db:
            db.append(user.id)
            await self.config.guild(server).db.set(db)
            await self.sendDiscordMessage(ctx, ":mage:Congrats!:mage:", "You have created your spellbook for **{}**, {}.".format(server.name, user.mention))
        else:
            await self.sendDiscordMessage(ctx, ":warning:Error:warning:", "Opps, it seems like you already have an account, {}.".format(user.mention))

    @commands.command(name="spellbook")
    @commands.guild_only()
    async def _acc(self, ctx, user: discord.Member = None):
        """Take a peek at your, or someone else's, spellbook."""

        server = ctx.guild
        db = await self.config.guild(server).db()
        user = user if user else ctx.author
        userdata = await self.config.member(user).all()
        pic = userdata["Characterpic"]

        Pages = []
        Pageno = 1

        for k, v in userdata.items():
            data = discord.Embed(colour=user.colour)
            # data.set_author(name="{}'s Account".format(user.name), icon_url=user.avatar_url)
            if v and not k == "Characterpic":
                if user.avatar_url and not pic:
                    if k == "Spell":
                        for page in list(pagify(str(v), delims=[","], page_length=600, shorten_by=50)):
                            data.set_author(
                                name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            page = listformatter(page)
                            data.add_field(name="Spells Known:",
                                           value=page, inline=False)
                            data.set_footer(
                                text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pages.append(data)
                    else:
                        data.set_author(
                            name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                        data.set_thumbnail(url=user.avatar_url)
                        data.add_field(name=k, value=v)
                        data.set_footer(
                            text=f"Page {Pageno} out of {len(userdata.items())}")
                        Pageno += 1
                        Pages.append(data)
                elif pic:
                    if k == "Spell":
                        for page in list(pagify(str(v), delims=[","], page_length=600, shorten_by=50)):
                            data.set_author(
                                name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            page = listformatter(page)
                            data.add_field(name="Spells Known:",
                                           value=page, inline=False)
                            data.set_footer(
                                text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pages.append(data)
                    else:
                        data.set_author(
                            name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                        data.set_thumbnail(url=user.avatar_url)
                        data.add_field(name=k, value=v)
                        data.set_footer(
                            text=f"Page {Pageno} out of {len(userdata.items())}")
                        Pageno += 1
                        Pages.append(data)

        if len(Pages) != 0:
            await menu(ctx, Pages, DEFAULT_CONTROLS)
        else:
            self.sendDiscordMessage(ctx, ":warning:Error:warning:",
                                    "{} doesn't have an account at the moment, sorry.".format(user.mention))

    @commands.group(name="add")
    @commands.guild_only()
    async def update(self):
        """Update your Spellbook"""
        pass

    @update.command()
    @commands.guild_only()
    async def spell(self, ctx, *, spell):
        """Which spell(s) do you want to add?"""

        # making a set so that duplicate spells in the same call are not considered
        new_spell_list = processStringToList(spell)
        new_spell_list_valid = []
        new_spell_list_invalid = []
        new_spell_list_duplicate = []
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        guild_group = self.config.member(user)
        db = await self.config.guild(server).db()
        userdata = await self.config.member(user).all()

        if user.id not in db:
            self.sendDiscordMessage(
                ctx, "Error:warning:", "Sadly, you can't add spells without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(prefix))
        else:
            totalSpellList = self.getAllSpells()
            for new_spell in new_spell_list:
                # checks if it's a valid spell
                if new_spell.upper() not in map(str.upper, totalSpellList):
                    new_spell_list_invalid.append(new_spell)
                    continue
                else:
                    # checks if the user already has this spell
                    if new_spell.upper() in map(str.upper, userdata["Spell"]):
                        new_spell_list_duplicate.append(new_spell)
                        continue
                    else:
                        new_spell_list_valid.append(string.capwords(new_spell))
                        continue

                        # save the valid spells, if any
            if(len(new_spell_list_valid) > 0):
                async with guild_group.Spell() as SpellGroup:
                    SpellGroup.extend(new_spell_list_valid)
                    SpellGroup.sort()
                    self.sendDiscordMessage(ctx, ":sparkles:Success!:sparkles:",
                                            "You have scribed the following spells into your Spellbook:\n{}".format(", ".join(new_spell_list_valid)))

                    # send the duplicate spells, if any
            if(len(new_spell_list_duplicate) > 0):
                self.sendDiscordMessage(ctx, ":coin:I'm saving you money!:coin:",
                                        "You already had these spells in your Spellbook: \n{}".format(", ".join(new_spell_list_duplicate)))

                # send the invalid spells, if any
            if(len(new_spell_list_invalid) > 0):
                self.sendDiscordMessage(ctx, ":warning:Oh no!:warning:",
                                        "The following spells are not valid:\n{}\nPlease make sure you spelled it right\nUsed ' and -'s correctly.\nPlease make sure your spell is in [this list](https://pastebin.com/YS7NmYqh)".format(", ".join(new_spell_list_invalid)))

    @commands.command()
    @commands.guild_only()
    async def remove(self, ctx, *, spell):
        """Rip pages from your spellbook, as hard as it is to do it"""

        # making a set so that duplicate spells in the same call are not considered
        new_spell_list = processStringToList(spell)
        new_spell_list_valid = []
        new_spell_list_invalid = []
        new_spell_list_unlearned = []
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()
        guild_group = self.config.member(user)
        userdata = await self.config.member(user).all()

        if user.id not in db:
            self.sendDiscordMessage(
                ctx, "Error:warning:", "Sadly, you can't add spells without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(prefix))
        else:
            totalSpellList = self.getAllSpells()
            for new_spell in new_spell_list:
                # checks if it's a valid spell
                if new_spell.upper() not in map(str.upper, totalSpellList):
                    new_spell_list_invalid.append(new_spell)
                    continue
                else:
                    # checks if the user already has this spell
                    if new_spell.upper() in map(str.upper, userdata["Spell"]):
                        new_spell_list_valid.append(new_spell)
                        continue
                    else:
                        new_spell_list_unlearned.append(
                            string.capwords(new_spell))
                        continue

                        # send the valid spells, if any
            if(len(new_spell_list_valid) > 0):
                async with guild_group.Spell() as SpellGroup:
                    for spell in new_spell_list_valid:
                        try:
                            SpellGroup.remove(spell)
                        except ValueError:
                            new_spell_list_valid.remove(spell)
                            pass
                    SpellGroup.sort()
                    self.sendDiscordMessage(ctx, ":sob:Success:sob:", value="You have ripped the pages of the following spells from your Spellbook:\n{}".format(
                        ", ".join(new_spell_list_valid)))

            # send the duplicate spells, if any
            if(len(new_spell_list_unlearned) > 0):
                self.sendDiscordMessage(ctx, ":question:Hmm?:question:", value="You don't have these spells in your Spellbook:\n{}".format(
                    ", ".join(new_spell_list_unlearned)))

                # send the invalid spells, if any
            if(len(new_spell_list_invalid) > 0):
                self.sendDiscordMessage(
                    ctx, ":warning:Oh no!:warning:", "The following spells are not valid:\n{}\nPlease make sure you spelled it right\nUsed ' and -'s correctly.\nPlease make sure your spell is in [this list](https://pastebin.com/YS7NmYqh)".format(", ".join(new_spell_list_invalid)))

    @commands.command()
    @commands.guild_only()
    async def filter(self, ctx, *, filter):
        """Searches for Wizards with knowledge of a particular spell"""

        filter = string.capwords(filter)
        server = ctx.guild
        db = await self.config.guild(server).db()
        FilteredList = []
        Pages = []
        Resultsperpage = 5
        PageNo = 1

        if len(db) == 0:
            await ctx.send("There are no spellbooks in this library")

        for id in db:
            user = server.get_member(id)
            nickname = user.display_name
            nickname = nickname[0:20]
            userdata = await self.config.member(user).all()

            if filter.upper() in map(str.upper, userdata["Spell"]):
                FilteredList.extend([[f"{nickname}", f"{user.id}"]])

        if len(FilteredList) == 0:
            await ctx.send("There isn't a single Wizard here that knows that spell")

        else:
            SplitList = [FilteredList[i * Resultsperpage:(i + 1) * Resultsperpage] for i in range(
                (len(FilteredList) + Resultsperpage - 1) // Resultsperpage)]
            for Split in SplitList:
                tabulatedlist = f"""```{tabulate(Split, headers=["#", "Username","ID"], tablefmt="fancy_grid", showindex="always", colalign=("center", "center", "center"))}```"""
                e = discord.Embed(colour=discord.Color.red())
                e.add_field(
                    name=f"Filter: {filter}", value=f"Number of results: {len(FilteredList)}", inline=False)
                e.add_field(name="Here is a list of all the Wizards who know that spell",
                            value=tabulatedlist, inline=False)
                e.set_footer(text=f"Page {PageNo}/{len(SplitList)}")
                PageNo += 1
                Pages.append(e)

            await menu(ctx, Pages, DEFAULT_CONTROLS)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def addallspells(self, ctx):
        """Adds all the spells to your Spellbook"""

        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()
        guild_group = self.config.member(user)
        spells = self.getAllSpells()

        if user.id not in db:
            self.sendDiscordMessage(
                ctx, "Error:warning:", "Sadly, you can't add spells without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(prefix))

        else:
            async with guild_group.Spell() as SpellGroup:
                SpellGroup.clear()
                self.spell(spells)
            self.sendDiscordMessage(ctx, ":sparkles:Success!:sparkles:",
                                    "You have scribed all the spells in existence into your Spellbook:")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def removeallspells(self, ctx):
        """It's almost as if you burnt the Spellbook"""

        server = ctx.guild
        user = ctx.author
        db = await self.config.guild(server).db()
        guild_group = self.config.member(user)

        if user.id not in db:
            self.sendDiscordMessage(
                ctx, "Error:warning:", "Sadly, you can't remove spells without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(ctx.prefix))
        else:
            async with guild_group.Spell() as SpellGroup:
                SpellGroup.clear()

            self.sendDiscordMessage(ctx, ":question:Congrats?:question:",
                                    value="You have removed all the Spells from your Spellbook")

    @addallspells.error
    async def addallspells_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(content=f"Chillout, You're on cooldown. Retry in {int(error.retry_after)} seconds", delete_after=int(error.retry_after))

    @removeallspells.error
    async def removeallspells_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(content=f"Chillout, Your on cooldown. Retry in {int(error.retry_after)} seconds", delete_after=int(error.retry_after))

    async def sendDiscordMessage(self, ctx, title, text):
        data = discord.Embed(colour=ctx.author.colour)
        data.add_field(name=title, value=text)
        await ctx.send(embed=data)

    # List of Spell https://pastebin.com/YS7NmYqh
    def getAllSpells(self):
        return ["Abi-Dalzim's Horrid Wilting", "Absorb Elements", "Aganazzar's Scorcher", "Alarm", "Alter Self", "Animate Dead", "Animate Objects", "Antimagic Field", "Antipathy/Sympathy", "Arcane Eye", "Arcane Gate", "Arcane Lock", "Ashardalon's Stride", "Astral Projection", "Augury", "Banishment", "Bestow Curse", "Bigby's Hand", "Blade of Disaster", "Blight", "Blindness/Deafness", "Blink", "Blur", "Borrowed Knowledge", "Burning Hands", "Catapult", "Catnap", "Cause Fear", "Chain Lightning", "Charm Monster", "Charm Person", "Chromatic Orb", "Circle of Death", "Clairvoyance", "Clone", "Cloud of Daggers", "Cloudkill", "Color Spray", "Comprehend Languages", "Cone of Cold", "Confusion", "Conjure Elemental", "Conjure Minor Elementals", "Contact Other Plane", "Contingency", "Continual Flame", "Control Water", "Control Weather", "Control Winds", "Counterspell", "Create Homunculus", "Create Magen", "Create Undead", "Creation", "Crown of Madness", "Crown of Stars", "Danse Macabre", "Darkness", "Darkvision", "Dawn", "Delayed Blast Fireball", "Demiplane", "Detect Magic", "Detect Thoughts", "Dimension Door", "Disguise Self", "Disintegrate", "Dispel Magic", "Distort Value", "Divination", "Dominate Monster", "Dominate Person", "Draconic Transformation", "Dragon's Breath", "Drawmij's Instant Summons", "Dream", "Dream of the Blue Veil", "Dust Devil", "Earth Tremor", "Earthbind", "Elemental Bane", "Enemies Abound", "Enervation", "Enhance Ability", "Enlarge/Reduce", "Erupting Earth", "Etherealness", "Evard's Black Tentacles", "Expeditious Retreat", "Eyebite", "Fabricate", "False Life", "Far Step", "Fast Friends", "Fear", "Feather Fall", "Feeblemind", "Feign Death", "Find Familiar", "Finger of Death", "Fire Shield", "Fireball", "Fizban's Platinum Shield", "Flame Arrows", "Flaming Sphere", "Flesh to Stone", "Fly", "Fog Cloud", "Forcecage", "Foresight", "Frost Fingers", "Gaseous Form", "Gate", "Geas", "Gentle Repose", "Gift of Gab", "Globe of Invulnerability", "Glyph of Warding", "Grease", "Greater Invisibility", "Guards and Wards", "Gust of Wind", "Hallucinatory Terrain", "Haste", "Hold Monster", "Hold Person", "Hypnotic Pattern", "Ice Knife", "Ice Storm", "Identify", "Illusory Dragon", "Illusory Script", "Immolation", "Imprisonment", "Incendiary Cloud", "Incite Greed", "Infernal Calling", "Intellect Fortress", "Investiture of Flame", "Investiture of Ice", "Investiture of Stone", "Investiture of Wind", "Invisibility", "Invulnerability", "Jim's Glowing Coin", "Jim's Magic Missile", "Jump", "Kinetic Jaunt", "Knock", "Legend Lore", "Leomund's Secret Chest", "Leomund's Tiny Hut", "Levitate", "Life Transference", "Lightning Bolt", "Locate Creature",
                "Locate Object", "Longstrider", "Maddening Darkness", "Mage Armor", "Magic Circle", "Magic Jar", "Magic Missile", "Magic Mouth", "Magic Weapon", "Major Image", "Mass Polymorph", "Mass Suggestion", "Maximilian's Earthen Grasp", "Maze", "Melf's Acid Arrow", "Melf's Minute Meteors", "Mental Prison", "Meteor Swarm", "Mighty Fortress", "Mind Blank", "Mind Spike", "Mirage Arcane", "Mirror Image", "Mislead", "Misty Step", "Modify Memory", "Mordenkainen's Faithful Hound", "Mordenkainen's Magnificent Mansion", "Mordenkainen's Private Sanctum", "Mordenkainen's Sword", "Move Earth", "Nathair's Mischief", "Negative Energy Flood", "Nondetection", "Nystul's Magic Aura", "Otiluke's Freezing Sphere", "Otiluke's Resilient Sphere", "Otto's Irresistible Dance", "Passwall", "Phantasmal Force", "Phantasmal Killer", "Phantom Steed", "Planar Binding", "Plane Shift", "Polymorph", "Power Word Kill", "Power Word Pain", "Power Word Stun", "Prismatic Spray", "Prismatic Wall", "Programmed Illusion", "Project Image", "Protection from Energy", "Protection from Evil and Good", "Psychic Scream", "Pyrotechnics", "Rary's Telepathic Bond", "Raulothim's Psychic Lance", "Ray of Enfeeblement", "Ray of Sickness", "Remove Curse", "Reverse Gravity", "Rime's Binding Ice", "Rope Trick", "Scatter", "Scorching Ray", "Scrying", "See Invisibility", "Seeming", "Sending", "Sequester", "Shadow Blade", "Shapechange", "Shatter", "Shield", "Sickening Radiance", "Silent Image", "Silvery Barbs", "Simulacrum", "Skill Empowerment", "Skywrite", "Sleep", "Sleet Storm", "Slow", "Snare", "Snilloc's Snowball Swarm", "Soul Cage", "Speak with Dead", "Spider Climb", "Spirit Shroud", "Steel Wind Strike", "Stinking Cloud", "Stone Shape", "Stoneskin", "Storm Sphere", "Suggestion", "Summon Aberration", "Summon Construct", "Summon Draconic Spirit", "Summon Elemental", "Summon Fey", "Summon Fiend", "Summon Greater Demon", "Summon Lesser Demons", "Summon Shadowspawn", "Summon Undead", "Sunbeam", "Sunburst", "Symbol", "Synaptic Static", "Tasha's Caustic Brew", "Tasha's Hideous Laughter", "Tasha's Mind Whip", "Tasha's Otherworldly Guise", "Telekinesis", "Telepathy", "Teleport", "Teleportation Circle", "Tenser's Floating Disk", "Tenser's Transformation", "Thunder Step", "Thunderwave", "Tidal Wave", "Time Stop", "Tiny Servant", "Tongues", "Transmute Rock", "True Polymorph", "True Seeing", "Unseen Servant", "Vampiric Touch", "Vitriolic Sphere", "Vortex Warp", "Wall of Fire", "Wall of Force", "Wall of Ice", "Wall of Light", "Wall of Sand", "Wall of Stone", "Wall of Water", "Warding Wind", "Water Breathing", "Watery Sphere", "Web", "Weird", "Whirlwind", "Wish", "Witch Bolt", "Wither and Bloom"]
