import discord
from discord import option
from discord.ext import commands, tasks
import datetime
import sqlite3 as sq3
import re
import os
import Database as db

intents = discord.Intents.default()
bot = commands.Bot(intents = intents)

with sq3.connect("userData.db") as conn:
    db.initialize_table(conn)

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")
    print('-' * 10, end = "\n")

reminder = bot.create_group("reminder", "Reminder related command")

@reminder.command(name = "set")
@option(
    name = "time",
    description = "Please use a format like '1d', '5h', '24m', or '100s'.",
)
@option(
    name = "reminder",
    description = "The reminder"
)
async def set(ctx: discord.context, time: str, reminder: str) -> None:
    "Set a reminder for yourself."
    time = time.lower()
    match = re.match(r"(\d+)([dhms])", time)
    if not match:
        await ctx.response.send_message("Invalid time format. Please use a format like '1d', '5h', '24m', or '100s'.")
        return
    
    amount = int(match.group(1))
    unit = match.group(2)

    now = datetime.datetime.now()
    if unit == "d":
        remind_time = now + datetime.timedelta(days = amount)
    elif unit == "h":
        remind_time = now + datetime.timedelta(hours = amount)
    elif unit == "m":
        remind_time = now + datetime.timedelta(minutes = amount)
    elif unit == "s":
        remind_time = now + datetime.timedelta(seconds = amount)
    else:
        await ctx.response.send_message("Invalid time unit. PLease use:\nd -> days\nh -> hours\nm -> minutes\ns -> seconds")
        return
    
    with sq3.connect("userData.db") as conn:
        db.insert(conn, ctx.author.id, remind_time.isoformat(), reminder)
    
    await ctx.response.send_message("Reminder set!")

@reminder.command(name = "view")
async def view(ctx: discord.context) -> None:
    "View your reminders"

    with sq3.connect("userData.db") as conn:
        data = db.view(conn, ctx.author.id)
        if len(data) < 1:
            await ctx.response.send_message("You don't have any reminders scheduled.")
            return
        
        embed=discord.Embed(title="Reminder list", description=f"{ctx.author.display_name}'s reminder", color=0x800080)
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.display_avatar}")
        
        for item in data:
            _, userId, time, message = item
            user = await bot.fetch_user(userId)
            time = datetime.datetime.fromisoformat(time)
            time = time.strftime("%A %d %B %Y, %H:%M:%S")

            embed.add_field(name="", value=f"{user.display_name} at {time}\n> {message}", inline=True)
        
        await ctx.response.send_message(embed=embed)

@tasks.loop(seconds = 1)
async def remind_task():
    now = datetime.datetime.now()
    with sq3.connect("userData.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE time <= ?", (now.isoformat(), ))
        reminders = cursor.fetchall()

        for reminder in reminders:
            reminderId, userId, time, message = reminder
            user = await bot.fetch_user(userId)

            if user:
                await user.send(f"Reminder!\n> {message}")
            
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminderId, ))
            conn.commit()

@remind_task.before_loop
async def before_remind_Task():
    await bot.wait_until_ready()

remind_task.start()
bot.run(os.getenv("BOT_TOKEN"))