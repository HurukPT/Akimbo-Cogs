import discord
import string
from tabulate import tabulate

from redbot.core import Config
from redbot.core import commands
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify

from .utils import *

class Account(commands.Cog):
    """The Account Cog"""

    def __init__(self, bot):
        self.bot = bot
        default_member = {
            "Age": None,
            "Site": None,
            "About": None,
            "Gender": None,
            "Job": None,
            "Email": None,
            "Other": None,
            "Characterpic": None,
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
        """Sign up to get your own account today!"""
        server = ctx.guild
        user = ctx.author
        db = await self.config.guild(server).db()
        if user.id not in db:
            db.append(user.id)
            await self.config.guild(server).db.set(db)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:", value="You have officially created your account for **{}**, {}.".format(server.name, user.mention))
            await ctx.send(embed=data)
        else: 
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Opps, it seems like you already have an account, {}.".format(user.mention))
            await ctx.send(embed=data)
    
    @commands.command(name="account")
    @commands.guild_only()
    async def _acc(self, ctx, user : discord.Member=None):
        """Your/Others Account"""
                    
        server = ctx.guild
        db = await self.config.guild(server).db()
        user = user if user else ctx.author
        userdata = await self.config.member(user).all()
        pic = userdata["Characterpic"]
  
        Pages=[]
        Pageno=1

        for k, v in userdata.items():
            data = discord.Embed(colour=user.colour)
            #data.set_author(name="{}'s Account".format(user.name), icon_url=user.avatar_url)
            if v and not k == "Characterpic":
                
                if user.avatar_url and not pic:
                    if k == "Spell":
                        for page in list(pagify(str(v), delims=[","], page_length=600, shorten_by=50)):
                            data.set_author(name=f"{str(user)}'s Account", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            page = listformatter(page)
                            data.add_field(name="Spells Known:", value=page, inline=False)
                            data.set_footer(text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pages.append(data)
                    else:
                            data.set_author(name=f"{str(user)}'s Account", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            data.add_field(name=k, value=v)
                            data.set_footer(text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pageno+=1
                            Pages.append(data)
                elif pic:
                    if k == "Spell":
                        for page in list(pagify(str(v), delims=[","], page_length=600, shorten_by=50)):
                            data.set_author(name=f"{str(user)}'s Account", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            page = listformatter(page)
                            data.add_field(name="Spells Known:", value=page, inline=False)
                            data.set_footer(text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pages.append(data)
                    else:
                            data.set_author(name=f"{str(user)}'s Account", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            data.add_field(name=k, value=v)
                            data.set_footer(text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pageno+=1
                            Pages.append(data)

        if len(Pages) != 0:
            await menu(ctx, Pages, DEFAULT_CONTROLS)
        else:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="{} doesn't have an account at the moment, sorry.".format(user.mention))
            await ctx.send(embed=data)

    @commands.group(name="update")
    @commands.guild_only()
    async def update(self, ctx):
        """Update your TPC"""
        pass

    @update.command()
    @commands.guild_only()
    async def about(self, ctx, *, about):
        """Tell us about yourself"""

        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()
        
        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)

        if len(about) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your about section is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)

        else:
            await self.config.member(user).About.set(about)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have updated your About Me to {}".format(about))
            await ctx.send(embed=data)

    @update.command()
    @commands.guild_only()
    async def website(self, ctx, *, site):
        """Do you have a website?"""
        
        server = ctx.guild
        user = ctx.message.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)
        
        if len(site) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your website is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)

        else:
            await self.config.member(user).Site.set(site)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your Website to {}".format(site))
            await ctx.send(embed=data)

    @update.command()
    @commands.guild_only()
    async def age(self, ctx, *, age):
        """How old are you?"""
        
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)

        if len(age) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your age is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)

        else:
            await self.config.member(user).Age.set(age)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your age to {}".format(age))
            await ctx.send(embed=data)

    @update.command()
    @commands.guild_only()
    async def job(self, ctx, *, job):
        """Do you have a job?"""
        
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)

        if len(job) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your job is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)

        else:
            await self.config.member(user).Job.set(job)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your Job to {}".format(job))
            await ctx.send(embed=data)
    
    @update.command()
    @commands.guild_only()
    async def gender(self, ctx, *, gender):
        """What's your gender?"""

        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)

        if len(gender) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your gender is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)            

        else:
            await self.config.member(user).Gender.set(gender)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your Gender to {}".format(gender))
            await ctx.send(embed=data)
 
    @update.command()
    @commands.guild_only()
    async def email(self, ctx, *, email):
        """What's your email address?"""
       
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)

        if len(email) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your email is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)

        else:
            await self.config.member(user).Email.set(email)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your Email to {}".format(email))
            await ctx.send(embed=data)

    @update.command()
    @commands.guild_only()
    async def other(self, ctx, *, other):
        """Incase you want to add anything else..."""
        
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)

        if len(other) > 1024:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Your other is too long. Please make it less than 1024 characters.")
            await ctx.send(embed=data)

        else:
            await self.config.member(user).Other.set(other)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your Other to {}".format(other))
            await ctx.send(embed=data)
            
    @update.command()
    @commands.guild_only()
    async def characterpic(self, ctx, *, characterpic):
        """What does your character look like?"""
        
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)
        else:
            await self.config.member(user).Characterpic.set(characterpic)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Congrats!:sparkles:",value="You have set your characterpic to {}".format(characterpic))
            data.set_image(url="{}".format(characterpic))
            await ctx.send(embed=data)

    @update.command()
    @commands.guild_only()
    async def spell(self, ctx, *, spell):
        """Which spell do you know?"""

        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        guild_group = self.config.member(user)
        db = await self.config.guild(server).db()
        userdata=await self.config.member(user).all()
        
        #List of Spell https://pastebin.com/YS7NmYqh
        spells=["Abi-Dalzim's Horrid Wilting", "Absorb Elements", "Aganazzar's Scorcher", "Alarm", "Alter Self", "Animate Dead", "Animate Objects", "Antimagic Field", "Antipathy/Sympathy", "Arcane Eye", "Arcane Gate", "Arcane Lock", "Ashardalon's Stride", "Astral Projection", "Augury", "Banishment", "Bestow Curse", "Bigby's Hand", "Blade of Disaster", "Blight", "Blindness/Deafness", "Blink", "Blur", "Borrowed Knowledge", "Burning Hands", "Catapult", "Catnap", "Cause Fear", "Chain Lightning", "Charm Monster", "Charm Person", "Chromatic Orb", "Circle of Death", "Clairvoyance", "Clone", "Cloud of Daggers", "Cloudkill", "Color Spray", "Comprehend Languages", "Cone of Cold", "Confusion", "Conjure Elemental", "Conjure Minor Elementals", "Contact Other Plane", "Contingency", "Continual Flame", "Control Water", "Control Weather", "Control Winds", "Counterspell", "Create Homunculus", "Create Magen", "Create Undead", "Creation", "Crown of Madness", "Crown of Stars", "Danse Macabre", "Darkness", "Darkvision", "Dawn", "Delayed Blast Fireball", "Demiplane", "Detect Magic", "Detect Thoughts", "Dimension Door", "Disguise Self", "Disintegrate", "Dispel Magic", "Distort Value", "Divination", "Dominate Monster", "Dominate Person", "Draconic Transformation", "Dragon's Breath", "Drawmij's Instant Summons", "Dream", "Dream of the Blue Veil", "Dust Devil", "Earth Tremor", "Earthbind", "Elemental Bane", "Enemies Abound", "Enervation", "Enhance Ability", "Enlarge/Reduce", "Erupting Earth", "Etherealness", "Evard's Black Tentacles", "Expeditious Retreat", "Eyebite", "Fabricate", "False Life", "Far Step", "Fast Friends", "Fear", "Feather Fall", "Feeblemind", "Feign Death", "Find Familiar", "Finger of Death", "Fire Shield", "Fireball", "Fizban's Platinum Shield", "Flame Arrows", "Flaming Sphere", "Flesh to Stone", "Fly", "Fog Cloud", "Forcecage", "Foresight", "Frost Fingers", "Gaseous Form", "Gate", "Geas", "Gentle Repose", "Gift of Gab", "Globe of Invulnerability", "Glyph of Warding", "Grease", "Greater Invisibility", "Guards and Wards", "Gust of Wind", "Hallucinatory Terrain", "Haste", "Hold Monster", "Hold Person", "Hypnotic Pattern", "Ice Knife", "Ice Storm", "Identify", "Illusory Dragon", "Illusory Script", "Immolation", "Imprisonment", "Incendiary Cloud", "Incite Greed", "Infernal Calling", "Intellect Fortress", "Investiture of Flame", "Investiture of Ice", "Investiture of Stone", "Investiture of Wind", "Invisibility", "Invulnerability", "Jim's Glowing Coin", "Jim's Magic Missile", "Jump", "Kinetic Jaunt", "Knock", "Legend Lore", "Leomund's Secret Chest", "Leomund's Tiny Hut", "Levitate", "Life Transference", "Lightning Bolt", "Locate Creature", "Locate Object", "Longstrider", "Maddening Darkness", "Mage Armor", "Magic Circle", "Magic Jar", "Magic Missile", "Magic Mouth", "Magic Weapon", "Major Image", "Mass Polymorph", "Mass Suggestion", "Maximilian's Earthen Grasp", "Maze", "Melf's Acid Arrow", "Melf's Minute Meteors", "Mental Prison", "Meteor Swarm", "Mighty Fortress", "Mind Blank", "Mind Spike", "Mirage Arcane", "Mirror Image", "Mislead", "Misty Step", "Modify Memory", "Mordenkainen's Faithful Hound", "Mordenkainen's Magnificent Mansion", "Mordenkainen's Private Sanctum", "Mordenkainen's Sword", "Move Earth", "Nathair's Mischief", "Negative Energy Flood", "Nondetection", "Nystul's Magic Aura", "Otiluke's Freezing Sphere", "Otiluke's Resilient Sphere", "Otto's Irresistible Dance", "Passwall", "Phantasmal Force", "Phantasmal Killer", "Phantom Steed", "Planar Binding", "Plane Shift", "Polymorph", "Power Word Kill", "Power Word Pain", "Power Word Stun", "Prismatic Spray", "Prismatic Wall", "Programmed Illusion", "Project Image", "Protection from Energy", "Protection from Evil and Good", "Psychic Scream", "Pyrotechnics", "Rary's Telepathic Bond", "Raulothim's Psychic Lance", "Ray of Enfeeblement", "Ray of Sickness", "Remove Curse", "Reverse Gravity", "Rime's Binding Ice", "Rope Trick", "Scatter", "Scorching Ray", "Scrying", "See Invisibility", "Seeming", "Sending", "Sequester", "Shadow Blade", "Shapechange", "Shatter", "Shield", "Sickening Radiance", "Silent Image", "Silvery Barbs", "Simulacrum", "Skill Empowerment", "Skywrite", "Sleep", "Sleet Storm", "Slow", "Snare", "Snilloc's Snowball Swarm", "Soul Cage", "Speak with Dead", "Spider Climb", "Spirit Shroud", "Steel Wind Strike", "Stinking Cloud", "Stone Shape", "Stoneskin", "Storm Sphere", "Suggestion", "Summon Aberration", "Summon Construct", "Summon Draconic Spirit", "Summon Elemental", "Summon Fey", "Summon Fiend", "Summon Greater Demon", "Summon Lesser Demons", "Summon Shadowspawn", "Summon Undead", "Sunbeam", "Sunburst", "Symbol", "Synaptic Static", "Tasha's Caustic Brew", "Tasha's Hideous Laughter", "Tasha's Mind Whip", "Tasha's Otherworldly Guise", "Telekinesis", "Telepathy", "Teleport", "Teleportation Circle", "Tenser's Floating Disk", "Tenser's Transformation", "Thunder Step", "Thunderwave", "Tidal Wave", "Time Stop", "Tiny Servant", "Tongues", "Transmute Rock", "True Polymorph", "True Seeing", "Unseen Servant", "Vampiric Touch", "Vitriolic Sphere", "Vortex Warp", "Wall of Fire", "Wall of Force", "Wall of Ice", "Wall of Light", "Wall of Sand", "Wall of Stone", "Wall of Water", "Warding Wind", "Water Breathing", "Watery Sphere", "Web", "Weird", "Whirlwind", "Wish", "Witch Bolt", "Wither and Bloom"]
 

        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)
        else:
            if spell.upper() in map(str.upper, spells):
                
                if (spell.upper() not in map(str.upper, userdata["Spell"])):
                    spell=string.capwords(spell)
                    async with guild_group.Spell() as SpellGroup:
                        SpellGroup.append(spell)
                    data = discord.Embed(colour=user.colour)
                    data.add_field(name="Congrats!:sparkles:",value="You have set your Spell to {}".format(spell))
                    await ctx.send(embed=data)
                elif spell.upper() in map(str.upper, userdata["Spell"]):
                    await ctx.send("That spell is already in your db")
          
            else:
                data = discord.Embed(colour=user.colour)
                data.add_field(name="Error:warning:",value="Please enter a valid spell.")
                data.add_field(name="Things to try:",value="Please make sure you spelled it right\nUsed ' and -'s correctly.\nPlease make sure your spell is in [this list](https://pastebin.com/YS7NmYqh)")
                await ctx.send(embed=data)

    @commands.command()
    @commands.guild_only()
    async def remove(self, ctx, category, *, value = None):
        """Removes the value from your category"""

        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()
        category=string.capwords(category)
        guild_group = self.config.member(user)
        userdata=await self.config.member(user).all()
        Fields=["Age","Site","About","Gender","Job","Email","Other","Characterpic","Spell"]
       
        if user.id not in db:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:warning:",value="Sadly, this feature is only available for people who had registered for an account. \n\nYou can register for a account today for free. All you have to do is say `{}signup` and you'll be all set.".format(prefix))
            await ctx.send(embed=data)
        else:
            if category.upper() in map(str.upper, Fields):
            
                if category == "Spell":
                    if value.upper() in map(str.upper, userdata[category]):
                        value=string.capwords(value)
                        async with guild_group.Spell() as SpellGroup:
                            SpellGroup.remove(value)
                        data = discord.Embed(colour=user.colour)
                        data.add_field(name="Congrats!:sparkles:",value="You have removed {} from your {}".format(value,category))
                        await ctx.send(embed=data)
                    else:
                        await ctx.send("That spell is not in your db")
                
                if category == "Age":
                    await self.config.member(user).Age.clear()
                if category == "Site":
                    await self.config.member(user).Site.clear()
                if category == "About":
                    await self.config.member(user).About.clear()
                if category == "Gender":
                    await self.config.member(user).Gender.clear()
                if category == "Job":
                    await self.config.member(user).Job.clear()
                if category == "Email":
                    await self.config.member(user).Email.clear()
                if category == "Other":
                    await self.config.member(user).Other.clear()
                
                data=discord.Embed(colour=user.colour)
                data.add_field(name="Congrats!:sparkles:",value="You have removed {} from your {}".format(value,category))
                await ctx.send(embed=data)

            else:
                await ctx.send("Not a valid category")

    @commands.command()
    @commands.guild_only()
    async def filter(self, ctx, category, *, filter):
        category=string.capwords(category)
        filter=string.capwords(filter)
        server = ctx.guild
        db = await self.config.guild(server).db()
        Fields=["Age","Site","About","Gender","Job","Email","Other","Characterpic","Spell"]
        FilteredList=[]
        Pages=[]
        Resultsperpage = 5
        PageNo = 1
        
        if len(db) == 0:
            await ctx.send("There are currently no users in the database")

        elif category in Fields:
            for id in db:
                user=server.get_member(id)
                nickname=user.display_name
                nickname=nickname[0:13]
                userdata=await self.config.member(user).all()
                if category == "Spell":
                    if filter.upper() in map(str.upper, userdata[category]):
                        FilteredList.extend([[f"{nickname}", f"{user.id}", f"{filter}"]]) 
                else:
                    if userdata[category] != None and userdata[category] == filter:
                        FilteredList.extend([[f"{nickname}", f"{user.id}", f"{filter}"]])

            if len(FilteredList) == 0:
                await ctx.send("No match found for your filters.")
                                
            if len(FilteredList) != 0:
                SplitList = [FilteredList[i * Resultsperpage:(i + 1) * Resultsperpage] for i in range((len(FilteredList) + Resultsperpage - 1) //Resultsperpage)] 
                for Split in SplitList:
                    tabulatedlist=f"""```{tabulate(Split, headers=["#", "Username","ID" , f"{category}"], tablefmt="fancy_grid", showindex="always", colalign=("center", "center", "center"))}```"""
                    e=discord.Embed(colour=discord.Color.red())
                    e.add_field(name="Here is a list of all the users match the filter", value=tabulatedlist)
                    e.set_footer(text=f"Page {PageNo}/{len(SplitList)}")
                    PageNo+=1
                    Pages.append(e)

                await menu(ctx, Pages, DEFAULT_CONTROLS)
        else:
            await ctx.send("Please enter a valid category")


