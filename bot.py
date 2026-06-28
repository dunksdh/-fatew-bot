import discord
from discord import app_commands
import aiohttp
import random
import re
import os
import json
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# =========================
# CONFIG - Using Environment Variables
# =========================
GUILD_ID = 1183585595835039765
GROUP_ID = 33209009
LOG_CHANNEL_ID = 1511325511261880441
ROOT_OWNER_ID = 386518904937381889

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
TOKEN = os.getenv("TOKEN") or "MTUxMTM4OTc2OTI1NzcxNzgyMA.GaYI0z.Y7P4qao1urKFrHaQ0ut3PopLaKFbF93jWXmg2c"
ROBLOSECURITY = os.getenv("ROBLOSECURITY") or "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhADIhsKBGR1aWQSEzE2Mjk4NDAyMjQwOTU0ODM5MDYoAw.CCZFq7pgL62nalbT93nb_2XxkTz9uMQiIUmKXkxH_lvVY37MT44IisaJjVyNMBWiG0OK4qarnzewbPVH88iB6if0Hshm2gf1Dwu2YsJGZX8dZmPf-0Lup4Fu244dvrGSn0J39-yhhcUcYmlz57BRi260jpGpAPAsMKc3uLqytBuvH2hYO1cbfb6bUSzzBhu0pOZtWzEzoK39YGK8z8f84dypI-P1V4eGRzef76arYN36LeHEs9RcylBqkdXKUSVc1Pk4K4UdsXZTOoOZYEmGyHgsspoFS_Xvb9WWwBAsNhhhjeJCWzCGF1Xwk7WjSZi2W_uqIh3rXp6jFMsvKF-3KWIAAC2l6Ts2zBeyWIVH7z33wByA_0ScB7EXYTxe_1xYh8BF_R4M9s-222DyRogn9Q7NRCjQ1Y600t0Bu1FVvoQVTdUq1phkotEEmidkaOoZs4qKvh0YiVifPrKqTJPrn53EEJr-f0IcIWLhkslvllpTWq-f4Q6OGjzJ6lQ8jKGvb2ruxvC-vi5haHgWNdvfrZCJx47wVzB9H3VRh3lJJXW0TsIDxLPlXnEiSun1td42-HzFRnXJa8Zvh9-4A5oUgTY_UAD4C9v5BnuHJzS5GnUWqYktVrdd1StHY5T1TqX78R8mtg-TrkXSVeHTXXOIaRTClo-kZiNeSe90rmKJj7TD_OVa2eIoR9XjsAPPl9dJYxXznn89ObZ-hFMyI4vEpwWVIUFkH-TJ8HOEt4xuk3e6eWkr4ifEVYYinrLtI4U8Siq5Lf__bZ5uOxmXI2dzJEIU5EiPRNQ6SSEBfKU1PxwShbMTEvva2S2Dy311okSfIYPZU0iV2ZSrp5Vz-lQY709TqaXWRmN-P7c0a00da8k4-3G1GvSSOWiVgDkCynaOWJDSpcS4dHpACNfu1_SXpsBD_YsbOuw_4vjPGAnIi09e4PLZ"

if not TOKEN:
    print("⚠️ Using hardcoded TOKEN (for local testing only)")
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

if not TOKEN:
    raise ValueError("TOKEN environment variable is not set!")
if not ROBLOSECURITY:
    print("⚠️ Warning: ROBLOSECURITY cookie not set. Ranking commands may fail.")

# Rest of your config stays the same
ENEMY_GROUP_IDS = {36075308, 3350380, 53050494}
ZHD_OWNER_ROLE_ID = 1508077165789450411
STAFF_ROLE_ID = 1510182006309261413
TRIAL_ROLE_ID = 1186222733982453770

# =========================
# CREDITS / MESSAGE SHOP
# =========================
CREDITS_PER_MESSAGE = 2          # credits earned per redeemed message
CREDITS_FILE = "credits.json"          # {user_id: credit_balance}
MSG_COUNT_FILE = "message_counts.json"  # {user_id: unredeemed_message_count}

# Roles purchasable with /creditrole, cheapest first. Trial is the entry tier —
# anyone holding Trial or any tier above it auto-receives STAFF_ROLE_ID (see
# on_member_update below). EDIT the role IDs for "rank_2"/"rank_3"/"rank_4" to
# match real roles in your server — these are placeholders.
CREDIT_ROLE_TIERS = [
    {"id": TRIAL_ROLE_ID, "name": "Trial", "cost": 1000},
    {"id": 1203254354144923668, "name": "Mod", "cost": 2000},
    {"id": 1510224416360108093, "name": "Head Mod", "cost": 4000},
    {"id": 1218372275355517058, "name": "Administrator", "cost": 6000},
    {"id": 1218371751747256380, "name": "Head Admin", "cost": 7000},
    {"id": 1219940929243189338, "name": "Management", "cost": 9000},
    {"id": 1510224936768376834, "name": "Head Management", "cost": 10000},
    {"id": 1186222717628854322, "name": "Community Manager", "cost": 12000},
    {"id": 1217435290692620378, "name": "Head of Staff", "cost": 20000},
]
CHECKSTAFF_SCAN_LIMIT = 5000  # messages per channel to scan
CHECKSTAFF_CHANNEL_IDS = {1515300686600998985}  # only scan these channels
BOT_START_TIME = time.time()

# Social lookup API keys (fill these in)
YOUTUBE_API_KEY = ""   # https://console.cloud.google.com — enable YouTube Data API v3
TWITCH_CLIENT_ID = ""  # https://dev.twitch.tv/console
TWITCH_CLIENT_SECRET = ""
STEAM_API_KEY = ""     # https://steamcommunity.com/dev/apikey

# =========================
# PERSISTENCE
# =========================
AUTH_FILE = "authorized_users.json"
ROLES_FILE = "saved_roles.json"
BANS_FILE = "ban_snapshot.json"
BLACKLIST_FILE = "blacklist.json"
OWNERS_FILE = "owners.json"
PROTECTED_FILE = "protected_users.json"
ANTINUKE_FILE = "antinuke_members.json"
ROLE_BLACKLIST_FILE = "role_blacklist.json"
IMAGE_BLACKLIST_FILE = "image_blacklist.json"
IMAGE_BLACKLIST_USERS_FILE = "image_blacklist_users.json"

# =========================
# ANTINUKE DEFAULTS
# =========================
ANTINUKE_DEFAULTS = {
    "role_create_limit": 2,
    "role_delete_limit": 2,
    "channel_create_limit": 2,
    "channel_delete_limit": 2,
    "vanity_change_limit": 1,
    "everyone_ping_limit": 1,
    "invite_spam_limit": 3,
    "window_seconds": 60,
}

DANGEROUS_PERMS = [
    "administrator",
    "manage_guild",
    "manage_roles",
    "manage_channels",
    "kick_members",
    "ban_members",
    "manage_webhooks",
    "manage_expressions",
    "mention_everyone",
]

def load_json(path: str, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f)

authorized_users: set = set(load_json(AUTH_FILE, []))
saved_roles: dict = {int(k): v for k, v in load_json(ROLES_FILE, {}).items()}
ban_snapshot: dict = {int(k): v for k, v in load_json(BANS_FILE, {}).items()}
blacklisted_users: dict = {int(k): v for k, v in load_json(BLACKLIST_FILE, {}).items()}
owners: set = set(load_json(OWNERS_FILE, [ROOT_OWNER_ID]))
protected_users: dict = {int(k): v for k, v in load_json(PROTECTED_FILE, {}).items()}
antinuke_members: dict = {int(k): v for k, v in load_json(ANTINUKE_FILE, {}).items()}
role_blacklist: dict = {int(k): {int(rk): rv for rk, rv in v.items()} for k, v in load_json(ROLE_BLACKLIST_FILE, {}).items()}
image_blacklist_words: list = load_json(IMAGE_BLACKLIST_FILE, ["lethal"])
image_blacklist_users: dict = {int(k): v for k, v in load_json(IMAGE_BLACKLIST_USERS_FILE, {}).items()}
credits: dict = {int(k): v for k, v in load_json(CREDITS_FILE, {}).items()}
message_counts: dict = {int(k): v for k, v in load_json(MSG_COUNT_FILE, {}).items()}
_antinuke_counters: dict = defaultdict(lambda: defaultdict(list))

# =========================
# AUTOPING STORAGE
# =========================
autoping_tasks: dict = {}

# =========================
# BOT SETUP
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
session: aiohttp.ClientSession = None
headers = {"User-Agent": "Mozilla/5.0"}

# =========================
# LOGGING
# =========================
async def send_log(guild, message: str):
    try:
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(message)
    except Exception as e:
        print(f"[LOG ERROR] {e}")

# =========================
# PERMISSIONS
# =========================
def is_owner(user_id: int) -> bool:
    return user_id in owners

def is_root_owner(user_id: int) -> bool:
    return user_id == ROOT_OWNER_ID

def is_authorized(user_id: int) -> bool:
    return user_id in authorized_users or is_owner(user_id)

def is_blacklisted(user_id: int) -> bool:
    return user_id in blacklisted_users

def save_role_blacklist():
    save_json(ROLE_BLACKLIST_FILE, {
        str(uid): {str(rid): info for rid, info in roles.items()}
        for uid, roles in role_blacklist.items()
    })

def save_image_blacklist_users():
    save_json(IMAGE_BLACKLIST_USERS_FILE, {str(k): v for k, v in image_blacklist_users.items()})

def save_credits():
    save_json(CREDITS_FILE, {str(k): v for k, v in credits.items()})

def save_message_counts():
    save_json(MSG_COUNT_FILE, {str(k): v for k, v in message_counts.items()})

async def image_contains_blacklisted_word(attachment: discord.Attachment, user_id: int):
    words = list(image_blacklist_words) + list(image_blacklist_users.get(user_id, []))
    if not OCR_AVAILABLE or not words:
        return None
    if not attachment.content_type or not attachment.content_type.startswith("image/"):
        return None
    try:
        img_bytes = await attachment.read()
        img = Image.open(BytesIO(img_bytes))
        text = pytesseract.image_to_string(img).lower()
        for word in words:
            if word.lower() in text:
                return word
    except Exception as e:
        print(f"[image_contains_blacklisted_word ERROR] {e}")
    return None

async def deny(interaction: discord.Interaction, roles: list[str]):
    embed = discord.Embed(title="Not Whitelisted", color=0xe74c3c)
    roles_fmt = ", ".join(f"`{r}`" for r in roles)
    embed.description = f"❌ | You are not whitelisted. You must be whitelisted as one of the following\nroles: {roles_fmt}."
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =========================
# ROBLOX API UTILITIES
# =========================
async def get_user_id(username: str):
    try:
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}
        async with session.post(url, json=payload, headers=headers) as r:
            data = await r.json()
            if not data.get("data"):
                return None
            return data["data"][0]["id"]
    except Exception as e:
        print(f"[get_user_id ERROR] {e}")
        return None

async def get_all_groups(user_id: int):
    try:
        url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data.get("data", [])
    except Exception as e:
        print(f"[get_all_groups ERROR] {e}")
        return []

async def get_roblox_avatar(user_id: int):
    try:
        url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data["data"][0]["imageUrl"]
    except Exception as e:
        print(f"[get_roblox_avatar ERROR] {e}")
        return None

async def get_roblox_full_body(user_id: int):
    try:
        url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=352x352&format=Png"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data["data"][0]["imageUrl"]
    except Exception as e:
        print(f"[get_roblox_full_body ERROR] {e}")
        return None

async def get_roblox_user_info(user_id: int):
    try:
        url = f"https://users.roblox.com/v1/users/{user_id}"
        async with session.get(url, headers=headers) as r:
            return await r.json()
    except Exception as e:
        print(f"[get_roblox_user_info ERROR] {e}")
        return None

async def get_friend_count(user_id: int):
    try:
        url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data.get("count", 0)
    except Exception as e:
        print(f"[get_friend_count ERROR] {e}")
        return 0

async def get_follower_count(user_id: int):
    try:
        url = f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data.get("count", 0)
    except Exception as e:
        print(f"[get_follower_count ERROR] {e}")
        return 0

async def get_following_count(user_id: int):
    try:
        url = f"https://friends.roblox.com/v1/users/{user_id}/followings/count"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data.get("count", 0)
    except Exception as e:
        print(f"[get_following_count ERROR] {e}")
        return 0

async def get_last_online(user_id: int) -> str:
    try:
        url = "https://presence.roblox.com/v1/presence/users"
        async with session.post(url, json={"userIds": [user_id]}, headers=headers) as r:
            data = await r.json()
            presences = data.get("userPresences", [])
            if presences:
                raw = presences[0].get("lastOnline", "")
                if raw:
                    dt = datetime.fromisoformat(raw.rstrip("Z"))
                    return dt.strftime("%-d %B %Y")
    except Exception as e:
        print(f"[get_last_online ERROR] {e}")
    return "Unknown"

async def get_badge_count(user_id: int) -> int:
    try:
        total = 0
        cursor = ""
        while True:
            url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Desc"
            if cursor:
                url += f"&cursor={cursor}"
            async with session.get(url, headers=headers) as r:
                data = await r.json()
            total += len(data.get("data", []))
            cursor = data.get("nextPageCursor")
            if not cursor:
                break
        return total
    except Exception as e:
        print(f"[get_badge_count ERROR] {e}")
        return 0

async def get_rap_and_value(user_id: int) -> tuple[int, int]:
    try:
        url = f"https://www.rolimons.com/playerapi/player/{user_id}"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            rap = data.get("player_rap", 0) or 0
            value = data.get("player_value", 0) or 0
            return rap, value
    except Exception as e:
        print(f"[get_rap_and_value ERROR] {e}")
        return 0, 0

# =========================
# READY EVENT
# =========================
@client.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    await tree.sync()
    print(f"✅ Logged in as {client.user}")

# =========================
# BLACKLIST + PROTECTION ENFORCEMENT — on_member_update
# =========================
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    guild = after.guild

    # ---- credits: trial (or any higher purchasable tier) grants staff automatically ----
    tier_role_ids = {t["id"] for t in CREDIT_ROLE_TIERS if t["id"]}
    roles_gained = set(after.roles) - set(before.roles)
    if any(r.id in tier_role_ids for r in roles_gained):
        staff_role = guild.get_role(STAFF_ROLE_ID)
        if staff_role and staff_role not in after.roles:
            try:
                await after.add_roles(staff_role, reason="Auto-granted: purchased Trial tier or above via /creditrole")
                await send_log(guild, f"⭐ **Auto-staff** — {after.mention} (`{after.id}`) was given {staff_role.mention} for holding a credit-shop tier role")
            except Exception as e:
                print(f"[on_member_update AUTOSTAFF ERROR] {e}")

    if is_blacklisted(after.id):
        zhd_owner_role = guild.get_role(ZHD_OWNER_ROLE_ID)
        if zhd_owner_role:
            roles_added = set(after.roles) - set(before.roles)
            roles_to_remove = [r for r in roles_added if r.position > zhd_owner_role.position]
            if roles_to_remove:
                try:
                    await after.remove_roles(*roles_to_remove, reason="Blacklisted user — role auto-removed")
                    log_msg = (
                        f"🚫 **Blacklist enforced** on {after.mention} (`{after.id}`): "
                        f"removed {', '.join(r.name for r in roles_to_remove)}"
                    )
                    await send_log(guild, log_msg)
                except Exception as e:
                    print(f"[on_member_update BLACKLIST ERROR] {e}")

    if after.id in role_blacklist:
        barred_role_ids = set(role_blacklist[after.id].keys())
        roles_added = set(after.roles) - set(before.roles)
        roles_to_strip = [r for r in roles_added if r.id in barred_role_ids]
        if roles_to_strip:
            try:
                await after.remove_roles(*roles_to_strip, reason="User is blacklisted from this role")
                log_msg = (
                    f"🚫 **Role blacklist enforced** on {after.mention} (`{after.id}`): "
                    f"removed {', '.join(r.name for r in roles_to_strip)}"
                )
                await send_log(guild, log_msg)
            except Exception as e:
                print(f"[on_member_update ROLE BLACKLIST ERROR] {e}")

    if after.id in protected_users and after.id not in saved_roles:
        protected_role_ids = set(protected_users[after.id]["role_ids"])
        roles_removed = set(before.roles) - set(after.roles)
        roles_to_restore = [r for r in roles_removed if r.id in protected_role_ids]
        if roles_to_restore:
            try:
                await after.add_roles(*roles_to_restore, reason="Protected user — role auto-restored")
                log_msg = (
                    f"🛡️ **Protection enforced** on {after.mention} (`{after.id}`): "
                    f"restored {', '.join(r.name for r in roles_to_restore)}"
                )
                await send_log(guild, log_msg)
            except Exception as e:
                print(f"[on_member_update PROTECTION ERROR] {e}")

# =========================
# /help
# =========================
@tree.command(name="help", description="List all commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Commands", color=discord.Color.blurple())
    embed.add_field(name="🎲 General", value="""
`/help` — Show this
`/botinfo` — Bot info
`/uptime` — How long the bot has been online
`/coinflip` — Flip a coin
`/avatar [member]` — Show a member's avatar
`/banner [member]` — Show a member's profile banner
`/userinfo [member]` — Show Discord info about a member
`/ship` — Ship two random server members together
`/rps` — Play rock paper scissors against the bot
`/github <username>` — Look up a GitHub profile
`/youtube <channel>` — Look up a YouTube channel
`/twitch <username>` — Look up a Twitch channel
`/tiktok <username>` — TikTok profile link
`/twitter <username>` — Twitter/X profile link
`/steam <username>` — Look up a Steam profile
`/redeemcredits` — Convert your messages into credits
`/creditrole shop` — View roles purchasable with credits
`/creditrole buy <tier>` — Buy a role with credits
""", inline=False)
    embed.add_field(name="🔵 Roblox", value="""
`/roblox <username>` — Full Roblox profile (RAP, badges, last online & more)
`/usertoid <username>` — Get Roblox ID
`/checkgroup <username>` — Check all groups + detect ours
`/groupinfo` — Show our Roblox group info
`/robloxinfo <username>` — Get full Roblox profile
`/enemygroup <username>` — Check if in enemy groups
""", inline=False)
    embed.add_field(name="⚠️ Authorized Only", value="""
`/striproles <member>` — Strip all roles (keeps /fatew)
`/restore <member>` — Restore stripped roles
`/snapshotbans` — Save current ban list
`/banlist` — View saved bans
`/unbanwave confirm:yes` — Unban everyone
`/rebanusers` — Reban snapshot users
`/blacklist <member> <reason>` — Blacklist a member
`/unblacklist <member>` — Remove from blacklist
`/viewblacklist` — View all blacklisted members
`/checkstaff` — View staff activity breakdown
`/addcredits <member> <amount>` — Manually adjust a member's credits
`/autoping start <member> [message]` — Ping a member every 20s
`/autoping stop [member]` — Stop autoping (omit member to stop all)
""", inline=False)
    embed.add_field(name="🔧 Prefix Commands (Authorized Only)", value="""
`,steal <emoji>` — Steal an emoji into this server
`,rank <username> <rank>` — Set a member's rank in the group
`,promote <username>` — Promote a member one rank
`,demote <username>` — Demote a member one rank
`,exile <username>` — Kick a member from the group
`,resetrank <username>` — Reset a member back to Member rank
""", inline=False)
    embed.add_field(name="👑 Owner Only", value="""
`/authorize <member>` — Grant admin access
`/unauthorize <member>` — Revoke admin access
`/addowner <member>` — Grant owner access
`/removeowner <member>` — Revoke owner access
`/protect <member>` — Protect a member's roles
`/unprotect <member>` — Remove role protection
`/viewprotected` — View all protected members
`/promotemod <member>` — Promote a mod to the next role above
`/antinuke setup <member>` — Put a member under antinuke watch
`/antinuke remove <member>` — Remove antinuke watch
`/antinuke info <member>` — View config & live counters
`/antinuke list` — View all watched members
`/resetallcredits confirm:yes` — Reset every member's credits to 0
`/roleroll [member]` — 1% chance to win the Admin Perms role
`/botstatus <type> <text>` — Change the bot's activity status
`/viewauthorized` — View all authorized users
`/viewowners` — View all owners
""", inline=False)
    embed.set_footer(text="Made by dunks")
    await interaction.response.send_message(embed=embed)

# =========================
# /botinfo
# =========================
@tree.command(name="botinfo", description="Show bot info")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Bot Info", color=discord.Color.blurple())
    embed.add_field(name="Guild ID", value=f"`{GUILD_ID}`", inline=True)
    embed.add_field(name="Group ID", value=f"`{GROUP_ID}`", inline=True)
    embed.add_field(name="Authorized Users", value=str(len(authorized_users)), inline=True)
    embed.add_field(name="Saved Role Snapshots", value=str(len(saved_roles)), inline=True)
    embed.add_field(name="Ban Snapshot Size", value=str(len(ban_snapshot)), inline=True)
    embed.add_field(name="Blacklisted Users", value=str(len(blacklisted_users)), inline=True)
    embed.add_field(name="Protected Users", value=str(len(protected_users)), inline=True)
    embed.add_field(name="Active Autopings", value=str(len(autoping_tasks)), inline=True)
    embed.add_field(name="AntiNuke Watched", value=str(len(antinuke_members)), inline=True)
    embed.set_footer(text="Made by dunks")
    await interaction.response.send_message(embed=embed)

# =========================
# /uptime
# =========================
@tree.command(name="uptime", description="Show how long the bot has been running")
async def uptime(interaction: discord.Interaction):
    elapsed = int(time.time() - BOT_START_TIME)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    embed = discord.Embed(title="⏱️ Uptime", color=discord.Color.green())
    embed.add_field(name="Running for", value=f"`{hours}h {minutes}m {seconds}s`", inline=False)
    await interaction.response.send_message(embed=embed)

# =========================
# /coinflip
# =========================
@tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(["🪙 Heads", "🪙 Tails"]))

# =========================
# /usertoid
# =========================
@tree.command(name="usertoid", description="Get a Roblox user's ID from their username")
async def usertoid(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    uid = await get_user_id(username)
    if not uid:
        return await interaction.followup.send("❌ User not found.")
    await interaction.followup.send(f"🔍 **{username}** → `{uid}`")

# =========================
# /enemygroup
# =========================
@tree.command(name="enemygroup", description="Check if a Roblox user is in enemy groups")
async def enemygroup(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    user_id = await get_user_id(username)
    if not user_id:
        return await interaction.followup.send("❌ User not found.")
    groups = await get_all_groups(user_id)
    user_group_ids = {g["group"]["id"] for g in groups}
    matched = user_group_ids & ENEMY_GROUP_IDS
    if matched:
        matched_names = [g["group"]["name"] for g in groups if g["group"]["id"] in matched]
        await interaction.followup.send(f"⚠️ **{username}** IS in an enemy group: {', '.join(matched_names)}")
    else:
        await interaction.followup.send(f"✅ **{username}** is NOT in any enemy groups.")

# =========================
# /checkgroup
# =========================
@tree.command(name="checkgroup", description="Check all Roblox groups for a user")
async def checkgroup(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    uid = await get_user_id(username)
    if not uid:
        return await interaction.followup.send("❌ User not found.")
    groups = await get_all_groups(uid)
    if not groups:
        return await interaction.followup.send(f"❌ {username} is not in any groups.")
    in_ours = False
    role_name = ""
    lines = []
    for g in groups:
        name = g["group"]["name"]
        gid = g["group"]["id"]
        role = g["role"]["name"]
        if gid == GROUP_ID:
            in_ours = True
            role_name = role
            lines.append(f"⭐ {name} (`{gid}`) — {role}  ← OUR GROUP")
        else:
            lines.append(f"• {name} (`{gid}`) — {role}")
    embed = discord.Embed(
        title=f"📋 Groups for {username}",
        color=discord.Color.green() if in_ours else discord.Color.red()
    )
    avatar_url = await get_roblox_avatar(uid)
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)
    if in_ours:
        embed.add_field(name="✅ In Our Group", value=f"Rank: **{role_name}**", inline=False)
    else:
        embed.add_field(name="❌ Not In Our Group", value="This user is not a member", inline=False)
    chunk = ""
    count = 1
    for line in lines:
        if len(chunk) + len(line) + 1 > 1024:
            embed.add_field(name=f"Groups ({count})", value=chunk, inline=False)
            chunk = line + "\n"
            count += 1
        else:
            chunk += line + "\n"
    if chunk:
        embed.add_field(name=f"Groups ({count})", value=chunk, inline=False)
    embed.set_footer(text=f"Roblox ID: {uid} | Total groups: {len(groups)}")
    await interaction.followup.send(embed=embed)

# =========================
# /groupinfo
# =========================
@tree.command(name="groupinfo", description="Show info about our Roblox group")
async def groupinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
    except Exception as e:
        print(f"[groupinfo ERROR] {e}")
        return await interaction.followup.send("❌ Could not fetch group info.")
    name = data.get("name", "Unknown")
    description = data.get("description", "").strip() or "No description"
    member_count = data.get("memberCount", 0)
    owner = data.get("owner")
    owner_name = owner.get("username", "Unknown") if owner else "Unknown"
    is_public = data.get("publicEntryAllowed", False)
    shout = data.get("shout")
    shout_text = shout.get("body", "").strip() if shout else None
    shout_poster = shout.get("poster", {}).get("username", "Unknown") if shout else None
    if len(description) > 300:
        description = description[:297] + "..."
    embed = discord.Embed(
        title=f"🏠 {name}",
        url=f"https://www.roblox.com/groups/{GROUP_ID}",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Members", value=f"`{member_count:,}`", inline=True)
    embed.add_field(name="Owner", value=owner_name, inline=True)
    embed.add_field(name="Entry", value="Open" if is_public else "Closed", inline=True)
    embed.add_field(name="Description", value=description, inline=False)
    if shout_text:
        embed.add_field(name=f"📢 Shout (by {shout_poster})", value=shout_text[:500], inline=False)
    embed.set_footer(text=f"Group ID: {GROUP_ID}")
    await interaction.followup.send(embed=embed)

# =========================
# /robloxinfo
# =========================
@tree.command(name="robloxinfo", description="Get full Roblox profile for a user")
async def robloxinfo(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    uid = await get_user_id(username)
    if not uid:
        return await interaction.followup.send("❌ User not found.")
    info = await get_roblox_user_info(uid)
    if not info:
        return await interaction.followup.send("❌ Could not fetch user info.")

    display_name = info.get("displayName", username)
    description = info.get("description", "").strip() or None
    created_raw = info.get("created", "")

    if created_raw:
        try:
            dt = datetime.fromisoformat(created_raw.rstrip("Z"))
            created = dt.strftime("%-d %B %Y")
        except Exception:
            created = created_raw[:10]
    else:
        created = "Unknown"

    avatar_url, last_online, badge_count, following, followers, rap_val = await asyncio.gather(
        get_roblox_full_body(uid),
        get_last_online(uid),
        get_badge_count(uid),
        get_following_count(uid),
        get_follower_count(uid),
        get_rap_and_value(uid),
    )
    rap, value = rap_val

    embed = discord.Embed(
        title=display_name,
        url=f"https://www.roblox.com/users/{uid}/profile",
        color=0x2b2d31
    )

    # Username as a blue clickable link above the description
    desc_parts = [f"[{username}](https://www.roblox.com/users/{uid}/profile)"]
    if description:
        desc_parts.append(description[:300])
    embed.description = "\n".join(desc_parts)

    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.add_field(name="Created", value=created, inline=True)
    embed.add_field(name="Last Online", value=last_online, inline=True)
    embed.add_field(name=f"Badges ({badge_count})", value="\u200b", inline=True)
    embed.add_field(name="RAP", value=f"[{rap:,}](https://www.rolimons.com/player/{uid})" if rap else "0", inline=True)
    embed.add_field(name="Value", value=f"[{value:,}](https://www.rolimons.com/player/{uid})" if value else "0", inline=True)
    embed.add_field(name="ID", value=str(uid), inline=True)
    embed.add_field(name="Following", value=str(following), inline=True)
    embed.add_field(name="Followers", value=str(followers), inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.set_footer(
        text="Roblox",
        icon_url="https://images.rbxcdn.com/6f17eb0bde00c12a9a0b0c79cf64a8ff"
    )

    await interaction.followup.send(embed=embed)

# =========================
# /roblox
# =========================
@tree.command(name="roblox", description="Look up a full Roblox profile")
@app_commands.describe(username="Roblox username to look up")
async def roblox(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    uid = await get_user_id(username)
    if not uid:
        return await interaction.followup.send("❌ User not found.")

    info = await get_roblox_user_info(uid)
    if not info:
        return await interaction.followup.send("❌ Could not fetch user info.")

    avatar_url, last_online, badge_count, following, followers, rap_val = await asyncio.gather(
        get_roblox_avatar(uid),
        get_last_online(uid),
        get_badge_count(uid),
        get_following_count(uid),
        get_follower_count(uid),
        get_rap_and_value(uid),
    )
    rap, value = rap_val

    display_name = info.get("displayName", username)
    description = info.get("description", "").strip() or None
    created_raw = info.get("created", "")
    is_banned = info.get("isBanned", False)

    if created_raw:
        try:
            dt = datetime.fromisoformat(created_raw.rstrip("Z"))
            created = dt.strftime("%-d %B %Y")
        except Exception:
            created = created_raw[:10]
    else:
        created = "Unknown"

    embed = discord.Embed(
        title=display_name,
        url=f"https://www.roblox.com/users/{uid}/profile",
        color=0xe8e8e8
    )
    if description:
        embed.description = description[:300]
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.add_field(name="Created", value=created, inline=True)
    embed.add_field(name="Last Online", value=last_online, inline=True)
    embed.add_field(name=f"Badges ({badge_count})", value="​", inline=True)
    embed.add_field(name="RAP", value=f"{rap:,}" if rap else "0", inline=True)
    embed.add_field(name="Value", value=f"{value:,}" if value else "0", inline=True)
    embed.add_field(name="ID", value=str(uid), inline=True)
    embed.add_field(name="Following", value=str(following), inline=True)
    embed.add_field(name="Followers", value=str(followers), inline=True)

    embed.set_footer(
        text="Roblox",
        icon_url="https://images.rbxcdn.com/6f17eb0bde00c12a9a0b0c79cf64a8ff"
    )

    await interaction.followup.send(embed=embed)

# =========================
# /authorize / /unauthorize
# =========================
@tree.command(name="authorize", description="Grant admin access", guild=discord.Object(id=GUILD_ID))
async def authorize(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    authorized_users.add(member.id)
    save_json(AUTH_FILE, list(authorized_users))
    await interaction.response.send_message(f"✅ {member.mention} authorized.")
    await send_log(interaction.guild, f"🔐 {member} authorized by {interaction.user}")

@tree.command(name="unauthorize", description="Revoke admin access", guild=discord.Object(id=GUILD_ID))
async def unauthorize(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    authorized_users.discard(member.id)
    save_json(AUTH_FILE, list(authorized_users))
    await interaction.response.send_message(f"🚫 {member.mention} unauthorized.")
    await send_log(interaction.guild, f"🚫 {member} unauthorized by {interaction.user}")

# =========================
# /addowner / /removeowner
# =========================
@tree.command(name="addowner", description="Grant owner access to a member", guild=discord.Object(id=GUILD_ID))
async def addowner(interaction: discord.Interaction, member: discord.Member):
    if not is_root_owner(interaction.user.id):
        return await deny(interaction, ["Root Owner"])
    if is_owner(member.id):
        return await interaction.response.send_message(f"⚠️ {member.mention} is already an owner.", ephemeral=True)
    owners.add(member.id)
    save_json(OWNERS_FILE, list(owners))
    embed = discord.Embed(title="👑 Owner Added", color=discord.Color.gold())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.set_footer(text="This member now has full owner permissions.")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"👑 {member} (`{member.id}`) granted owner by {interaction.user}")

@tree.command(name="removeowner", description="Revoke owner access from a member", guild=discord.Object(id=GUILD_ID))
async def removeowner(interaction: discord.Interaction, member: discord.Member):
    if not is_root_owner(interaction.user.id):
        return await deny(interaction, ["Root Owner"])
    if member.id == ROOT_OWNER_ID:
        return await interaction.response.send_message("❌ Cannot remove the root owner.", ephemeral=True)
    if not is_owner(member.id):
        return await interaction.response.send_message(f"⚠️ {member.mention} is not an owner.", ephemeral=True)
    owners.discard(member.id)
    save_json(OWNERS_FILE, list(owners))
    embed = discord.Embed(title="🚫 Owner Removed", color=discord.Color.red())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"🚫 {member} (`{member.id}`) owner removed by {interaction.user}")

# =========================
# /striproles
# =========================
@tree.command(name="striproles", description="Remove all roles except /fatew", guild=discord.Object(id=GUILD_ID))
async def striproles(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    await interaction.response.defer()

    fatew_role = interaction.guild.get_role(1186222747878174780)
    if not fatew_role:
        return await interaction.followup.send("❌ /fatew role not found.")

    bot_top_role = interaction.guild.me.top_role

    roles_to_save = [
        r.id for r in member.roles
        if r != interaction.guild.default_role and r != fatew_role
    ]
    saved_roles[member.id] = roles_to_save
    save_json(ROLES_FILE, {str(k): v for k, v in saved_roles.items()})

    remove_roles = [
        r for r in member.roles
        if r != interaction.guild.default_role
        and r != fatew_role
        and r.position < bot_top_role.position
    ]

    skipped_roles = [
        r for r in member.roles
        if r != interaction.guild.default_role
        and r != fatew_role
        and r.position >= bot_top_role.position
    ]

    if remove_roles:
        await member.remove_roles(*remove_roles, reason=f"Roles stripped by {interaction.user}")

    await member.add_roles(fatew_role)

    msg = f"🧨 Roles stripped from {member.mention}"
    if skipped_roles:
        msg += (
            f"\n⚠️ Could not remove the following roles as they are above the bot in the hierarchy: "
            f"{', '.join(f'`{r.name}`' for r in skipped_roles)}\n"
            f"➡️ Move the bot's role higher in **Server Settings → Roles** to fix this."
        )

    await interaction.followup.send(msg)
    await send_log(interaction.guild, f"🧨 Roles stripped from {member} by {interaction.user}")

# =========================
# /restore
# =========================
@tree.command(name="restore", description="Restore stripped roles", guild=discord.Object(id=GUILD_ID))
async def restore(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    await interaction.response.defer()
    role_ids = saved_roles.get(member.id)
    if not role_ids:
        return await interaction.followup.send("❌ No saved roles for this member.")
    fatew_role = interaction.guild.get_role(1186222747878174780)
    if fatew_role and fatew_role in member.roles:
        await member.remove_roles(fatew_role)
    roles = [interaction.guild.get_role(rid) for rid in role_ids if interaction.guild.get_role(rid)]
    await member.add_roles(*roles)
    del saved_roles[member.id]
    save_json(ROLES_FILE, {str(k): v for k, v in saved_roles.items()})
    await interaction.followup.send(f"🔁 Roles restored for {member.mention}")
    await send_log(interaction.guild, f"🔁 Roles restored for {member} by {interaction.user}")

# =========================
# /snapshotbans
# =========================
@tree.command(name="snapshotbans", description="Save current ban list", guild=discord.Object(id=GUILD_ID))
async def snapshotbans(interaction: discord.Interaction):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    await interaction.response.defer()
    bans = [b async for b in interaction.guild.bans()]
    ban_snapshot.clear()
    for b in bans:
        ban_snapshot[b.user.id] = str(b.user)
    save_json(BANS_FILE, {str(k): v for k, v in ban_snapshot.items()})
    await interaction.followup.send(f"📸 Saved {len(ban_snapshot)} bans.")

# =========================
# /banlist
# =========================
@tree.command(name="banlist", description="Show saved bans", guild=discord.Object(id=GUILD_ID))
async def banlist(interaction: discord.Interaction):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    await interaction.response.defer(ephemeral=True)
    if not ban_snapshot:
        return await interaction.followup.send("📭 No snapshot saved.")

    lines = [f"`{uid}` → {name}" for uid, name in ban_snapshot.items()]
    total = len(lines)

    if total > 50:
        content = "\n".join(lines)
        file = discord.File(
            fp=__import__("io").BytesIO(content.encode()),
            filename="banlist.txt"
        )
        await interaction.followup.send(f"📋 Ban snapshot — {total} entries:", file=file)
    else:
        embeds = []
        chunk = ""
        page = 1
        for line in lines:
            if len(chunk) + len(line) + 1 > 4096:
                e = discord.Embed(title=f"📋 Ban Snapshot ({total}) — Page {page}", color=discord.Color.red())
                e.description = chunk
                embeds.append(e)
                chunk = line + "\n"
                page += 1
            else:
                chunk += line + "\n"
        if chunk:
            e = discord.Embed(title=f"📋 Ban Snapshot ({total})" + (f" — Page {page}" if page > 1 else ""), color=discord.Color.red())
            e.description = chunk
            embeds.append(e)
        for e in embeds:
            await interaction.followup.send(embed=e)

# =========================
# /unbanwave
# =========================
@tree.command(name="unbanwave", description="Unban all users — requires confirm:yes", guild=discord.Object(id=GUILD_ID))
async def unbanwave(interaction: discord.Interaction, confirm: str):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if confirm.lower() != "yes":
        return await interaction.response.send_message("⚠️ Type `yes` in the confirm field to proceed.", ephemeral=True)
    await interaction.response.defer()
    bans = [b async for b in interaction.guild.bans()]
    count = 0
    for b in bans:
        try:
            await interaction.guild.unban(b.user)
            count += 1
        except Exception as e:
            print(f"[unbanwave ERROR] {e}")
    await interaction.followup.send(f"✅ Unbanned {count} users.")
    await send_log(interaction.guild, f"🌊 Unban wave by {interaction.user}: {count} users unbanned")

# =========================
# /rebanusers
# =========================
@tree.command(name="rebanusers", description="Reban all users from snapshot", guild=discord.Object(id=GUILD_ID))
async def rebanusers(interaction: discord.Interaction):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    await interaction.response.defer()
    count = 0
    for user_id in ban_snapshot.keys():
        try:
            user = await client.fetch_user(user_id)
            await interaction.guild.ban(user, reason="Reban snapshot")
            count += 1
        except Exception as e:
            print(f"[rebanusers ERROR] {e}")
    await interaction.followup.send(f"🔁 Rebanned {count} users.")
    await send_log(interaction.guild, f"🔁 Reban wave by {interaction.user}: {count} users rebanned")

# =========================
# /blacklist
# =========================
@tree.command(name="blacklist", description="Blacklist a member — prevents them from holding roles above ZHD Owner", guild=discord.Object(id=GUILD_ID))
async def blacklist(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if is_owner(member.id):
        return await interaction.response.send_message("❌ Cannot blacklist the owner.", ephemeral=True)
    if is_blacklisted(member.id):
        return await interaction.response.send_message(f"⚠️ {member.mention} is already blacklisted.", ephemeral=True)
    blacklisted_users[member.id] = {
        "username": str(member),
        "reason": reason,
        "blacklisted_by": str(interaction.user),
        "blacklisted_at": datetime.now(timezone.utc).isoformat()
    }
    save_json(BLACKLIST_FILE, {str(k): v for k, v in blacklisted_users.items()})
    guild = interaction.guild
    zhd_owner_role = guild.get_role(ZHD_OWNER_ROLE_ID)
    removed = []
    if zhd_owner_role:
        roles_to_remove = [r for r in member.roles if r.position > zhd_owner_role.position]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason=f"Blacklisted by {interaction.user}: {reason}")
            removed = [r.name for r in roles_to_remove]
    embed = discord.Embed(title="🚫 Member Blacklisted", color=discord.Color.red())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    if removed:
        embed.add_field(name="Roles Removed", value=", ".join(removed), inline=False)
    else:
        embed.add_field(name="Roles Removed", value="None (no roles above ZHD Owner)", inline=False)
    embed.set_footer(text="Future role assignments above ZHD Owner will be auto-removed.")
    await interaction.response.send_message(embed=embed)
    await send_log(guild, f"🚫 {member} (`{member.id}`) blacklisted by {interaction.user} — Reason: {reason}")

# =========================
# /unblacklist
# =========================
@tree.command(name="unblacklist", description="Remove a member from the blacklist", guild=discord.Object(id=GUILD_ID))
async def unblacklist(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if not is_blacklisted(member.id):
        return await interaction.response.send_message(f"⚠️ {member.mention} is not blacklisted.", ephemeral=True)
    entry = blacklisted_users.pop(member.id)
    save_json(BLACKLIST_FILE, {str(k): v for k, v in blacklisted_users.items()})
    embed = discord.Embed(title="✅ Member Unblacklisted", color=discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Original Reason", value=entry.get("reason", "Unknown"), inline=False)
    embed.add_field(name="Originally Blacklisted By", value=entry.get("blacklisted_by", "Unknown"), inline=True)
    embed.set_footer(text="This member can now receive roles normally.")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"✅ {member} (`{member.id}`) unblacklisted by {interaction.user}")

# =========================
# /viewblacklist
# =========================
@tree.command(name="viewblacklist", description="View all blacklisted members", guild=discord.Object(id=GUILD_ID))
async def viewblacklist(interaction: discord.Interaction):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if not blacklisted_users:
        return await interaction.response.send_message("📭 No one is currently blacklisted.", ephemeral=True)

    entries = []
    for uid, entry in blacklisted_users.items():
        ts = entry.get("blacklisted_at", "Unknown")
        if ts != "Unknown":
            try:
                dt = datetime.fromisoformat(ts)
                ts = dt.strftime("%d/%m/%Y")
            except Exception:
                pass
        entries.append(
            f"<@{uid}> (`{uid}`)\n"
            f"**Reason:** {entry.get('reason', 'Unknown')} — **By:** {entry.get('blacklisted_by', 'Unknown')} — **Date:** {ts}\n"
        )

    embeds = []
    page_text = ""
    page = 1
    for entry_text in entries:
        if len(page_text) + len(entry_text) + 1 > 4000:
            e = discord.Embed(title=f"🚫 Blacklisted Members — Page {page}", color=discord.Color.red())
            e.description = page_text
            e.set_footer(text=f"Total: {len(blacklisted_users)}")
            embeds.append(e)
            page_text = entry_text + "\n"
            page += 1
        else:
            page_text += entry_text + "\n"
    if page_text:
        title = "🚫 Blacklisted Members" + (f" — Page {page}" if page > 1 else "")
        e = discord.Embed(title=title, color=discord.Color.red())
        e.description = page_text
        e.set_footer(text=f"Total: {len(blacklisted_users)}")
        embeds.append(e)

    await interaction.response.send_message(embed=embeds[0], ephemeral=True)
    for e in embeds[1:]:
        await interaction.followup.send(embed=e, ephemeral=True)

# =========================
# /blacklistgivenrole
# =========================
@tree.command(name="blacklistgivenrole", description="Bar a member from holding a specific role — auto-removed if assigned", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="Member to restrict", role="Role they may never hold", reason="Reason for the restriction")
async def blacklistgivenrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role, reason: str = "No reason provided"):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if is_owner(member.id):
        return await interaction.response.send_message("❌ Cannot restrict the owner.", ephemeral=True)
    existing = role_blacklist.setdefault(member.id, {})
    if role.id in existing:
        return await interaction.response.send_message(f"⚠️ {member.mention} is already barred from {role.mention}.", ephemeral=True)
    existing[role.id] = {
        "reason": reason,
        "by": str(interaction.user),
        "at": datetime.now(timezone.utc).isoformat()
    }
    save_role_blacklist()

    removed = False
    if role in member.roles:
        try:
            await member.remove_roles(role, reason=f"Role-blacklisted by {interaction.user}: {reason}")
            removed = True
        except Exception as e:
            print(f"[blacklistgivenrole REMOVE ERROR] {e}")

    embed = discord.Embed(title="🚫 Role Restriction Added", color=discord.Color.red())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Role", value=role.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    if removed:
        embed.add_field(name="Note", value=f"Removed {role.mention} immediately (member already had it).", inline=False)
    embed.set_footer(text="This role will be auto-removed if assigned again, by anyone.")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"🚫 {member} (`{member.id}`) barred from role {role.name} by {interaction.user} — Reason: {reason}")

# =========================
# /unblacklistgivenrole
# =========================
@tree.command(name="unblacklistgivenrole", description="Remove a member's restriction on a specific role", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="Member to unrestrict", role="Role to allow again")
async def unblacklistgivenrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if member.id not in role_blacklist or role.id not in role_blacklist[member.id]:
        return await interaction.response.send_message(f"⚠️ {member.mention} is not barred from {role.mention}.", ephemeral=True)
    entry = role_blacklist[member.id].pop(role.id)
    if not role_blacklist[member.id]:
        del role_blacklist[member.id]
    save_role_blacklist()

    embed = discord.Embed(title="✅ Role Restriction Removed", color=discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Role", value=role.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Original Reason", value=entry.get("reason", "Unknown"), inline=False)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"✅ {member} (`{member.id}`) role restriction on {role.name} removed by {interaction.user}")

# =========================
# /viewroleblacklist
# =========================
@tree.command(name="viewroleblacklist", description="View a member's role restrictions", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="Member to check")
async def viewroleblacklist(interaction: discord.Interaction, member: discord.Member):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    entries = role_blacklist.get(member.id)
    if not entries:
        return await interaction.response.send_message(f"📭 {member.mention} has no role restrictions.", ephemeral=True)
    embed = discord.Embed(title=f"🚫 Role Restrictions — {member}", color=discord.Color.orange())
    guild = interaction.guild
    for rid, info in entries.items():
        role = guild.get_role(rid)
        role_name = role.mention if role else f"`{rid}` (deleted role)"
        embed.add_field(
            name=role_name,
            value=f"**Reason:** {info.get('reason', 'Unknown')} — **By:** {info.get('by', 'Unknown')}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# =========================
# /imageblacklist
# =========================
@tree.command(name="imageblacklistadd", description="Add a word — images containing it (via OCR) will be auto-deleted", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(word="Word to block in images", member="Optional — only block this word for this specific user")
async def imageblacklistadd(interaction: discord.Interaction, word: str, member: discord.Member = None):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    if not OCR_AVAILABLE:
        return await interaction.response.send_message(
            "❌ OCR isn't installed on this bot's host. Install it with:\n`pip install pytesseract pillow` and ensure the `tesseract` binary is on PATH.",
            ephemeral=True
        )
    word = word.strip().lower()
    if not word:
        return await interaction.response.send_message("❌ Word can't be empty.", ephemeral=True)

    if member:
        user_words = image_blacklist_users.setdefault(member.id, [])
        if word in [w.lower() for w in user_words]:
            return await interaction.response.send_message(f"⚠️ `{word}` is already blacklisted for {member.mention}.", ephemeral=True)
        user_words.append(word)
        save_image_blacklist_users()
        await interaction.response.send_message(f"✅ Added `{word}` to {member.mention}'s personal image blacklist.")
        await send_log(interaction.guild, f"🖼️ {interaction.user} added `{word}` to {member}'s ({member.id}) personal image blacklist.")
        return

    if word in [w.lower() for w in image_blacklist_words]:
        return await interaction.response.send_message(f"⚠️ `{word}` is already blacklisted.", ephemeral=True)
    image_blacklist_words.append(word)
    save_json(IMAGE_BLACKLIST_FILE, image_blacklist_words)
    await interaction.response.send_message(f"✅ Added `{word}` to the server-wide image blacklist.")
    await send_log(interaction.guild, f"🖼️ {interaction.user} added `{word}` to the image blacklist.")

@tree.command(name="imageblacklistremove", description="Remove a word from the image blacklist", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(word="Word to unblock", member="Optional — only remove from this specific user's personal list")
async def imageblacklistremove(interaction: discord.Interaction, word: str, member: discord.Member = None):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])
    word = word.strip().lower()

    if member:
        user_words = image_blacklist_users.get(member.id, [])
        matches = [w for w in user_words if w.lower() == word]
        if not matches:
            return await interaction.response.send_message(f"⚠️ `{word}` is not on {member.mention}'s personal image blacklist.", ephemeral=True)
        for m in matches:
            user_words.remove(m)
        if not user_words:
            image_blacklist_users.pop(member.id, None)
        save_image_blacklist_users()
        await interaction.response.send_message(f"✅ Removed `{word}` from {member.mention}'s personal image blacklist.")
        await send_log(interaction.guild, f"🖼️ {interaction.user} removed `{word}` from {member}'s ({member.id}) personal image blacklist.")
        return

    matches = [w for w in image_blacklist_words if w.lower() == word]
    if not matches:
        return await interaction.response.send_message(f"⚠️ `{word}` is not on the image blacklist.", ephemeral=True)
    for m in matches:
        image_blacklist_words.remove(m)
    save_json(IMAGE_BLACKLIST_FILE, image_blacklist_words)
    await interaction.response.send_message(f"✅ Removed `{word}` from the server-wide image blacklist.")
    await send_log(interaction.guild, f"🖼️ {interaction.user} removed `{word}` from the image blacklist.")

@tree.command(name="imageblacklistview", description="View blocked words (server-wide, or for one user)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="Optional — view this user's personal list instead of the server-wide list")
async def imageblacklistview(interaction: discord.Interaction, member: discord.Member = None):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])

    if member:
        user_words = image_blacklist_users.get(member.id, [])
        if not user_words:
            return await interaction.response.send_message(f"📭 {member.mention} has no personal image-blocked words.", ephemeral=True)
        embed = discord.Embed(title=f"🖼️ Image-Blocked Words — {member}", color=discord.Color.orange())
        embed.description = ", ".join(f"`{w}`" for w in user_words)
        if not OCR_AVAILABLE:
            embed.set_footer(text="⚠️ OCR library not installed — enforcement is currently inactive.")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if not image_blacklist_words:
        return await interaction.response.send_message("📭 No words are currently blacklisted server-wide for images.", ephemeral=True)
    embed = discord.Embed(title="🖼️ Image-Blocked Words (Server-Wide)", color=discord.Color.orange())
    embed.description = ", ".join(f"`{w}`" for w in image_blacklist_words)
    if not OCR_AVAILABLE:
        embed.set_footer(text="⚠️ OCR library not installed — enforcement is currently inactive.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =========================
# /protect
# =========================
@tree.command(name="protect", description="Protect a member's current roles — they'll be auto-restored if removed", guild=discord.Object(id=GUILD_ID))
async def protect(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if member.id in protected_users:
        return await interaction.response.send_message(f"⚠️ {member.mention} is already protected.", ephemeral=True)
    role_ids = [r.id for r in member.roles if r != interaction.guild.default_role]
    role_names = [r.name for r in member.roles if r != interaction.guild.default_role]
    protected_users[member.id] = {
        "username": str(member),
        "reason": reason,
        "protected_by": str(interaction.user),
        "protected_at": datetime.now(timezone.utc).isoformat(),
        "role_ids": role_ids
    }
    save_json(PROTECTED_FILE, {str(k): v for k, v in protected_users.items()})
    embed = discord.Embed(title="🛡️ Member Protected", color=discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Protected Roles", value=", ".join(role_names) if role_names else "None", inline=False)
    embed.set_footer(text="Any of these roles that get removed will be instantly restored.")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"🛡️ {member} (`{member.id}`) protected by {interaction.user} — Reason: {reason}")

# =========================
# /unprotect
# =========================
@tree.command(name="unprotect", description="Remove role protection from a member", guild=discord.Object(id=GUILD_ID))
async def unprotect(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if member.id not in protected_users:
        return await interaction.response.send_message(f"⚠️ {member.mention} is not protected.", ephemeral=True)
    entry = protected_users.pop(member.id)
    save_json(PROTECTED_FILE, {str(k): v for k, v in protected_users.items()})
    embed = discord.Embed(title="✅ Protection Removed", color=discord.Color.orange())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Original Reason", value=entry.get("reason", "Unknown"), inline=False)
    embed.add_field(name="Originally Protected By", value=entry.get("protected_by", "Unknown"), inline=True)
    embed.set_footer(text="This member's roles can now be freely modified.")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"✅ {member} (`{member.id}`) unprotected by {interaction.user}")

# =========================
# /viewprotected
# =========================
@tree.command(name="viewprotected", description="View all protected members", guild=discord.Object(id=GUILD_ID))
async def viewprotected(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if not protected_users:
        return await interaction.response.send_message("📭 No one is currently protected.", ephemeral=True)

    entries = []
    for uid, entry in protected_users.items():
        ts = entry.get("protected_at", "Unknown")
        if ts != "Unknown":
            try:
                dt = datetime.fromisoformat(ts)
                ts = dt.strftime("%d/%m/%Y")
            except Exception:
                pass
        role_ids = entry.get("role_ids", [])
        role_names = []
        for rid in role_ids:
            role = interaction.guild.get_role(rid)
            role_names.append(role.name if role else f"Deleted ({rid})")
        entries.append(
            f"<@{uid}> (`{uid}`)\n"
            f"**Reason:** {entry.get('reason', 'Unknown')} — **By:** {entry.get('protected_by', 'Unknown')} — **Date:** {ts}\n"
            f"**Roles:** {', '.join(role_names) if role_names else 'None'}\n"
        )

    embeds = []
    page_text = ""
    page = 1
    for entry_text in entries:
        if len(page_text) + len(entry_text) + 1 > 4000:
            e = discord.Embed(title=f"🛡️ Protected Members — Page {page}", color=discord.Color.green())
            e.description = page_text
            e.set_footer(text=f"Total: {len(protected_users)}")
            embeds.append(e)
            page_text = entry_text + "\n"
            page += 1
        else:
            page_text += entry_text + "\n"
    if page_text:
        title = "🛡️ Protected Members" + (f" — Page {page}" if page > 1 else "")
        e = discord.Embed(title=title, color=discord.Color.green())
        e.description = page_text
        e.set_footer(text=f"Total: {len(protected_users)}")
        embeds.append(e)

    await interaction.response.send_message(embed=embeds[0], ephemeral=True)
    for e in embeds[1:]:
        await interaction.followup.send(embed=e, ephemeral=True)

# =========================
# /promotemod
# =========================
@tree.command(name="promotemod", description="Promote a mod to the next role above in the server", guild=discord.Object(id=GUILD_ID))
async def promotemod(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])

    bot_top_role = interaction.guild.me.top_role

    current_role = next(
        (r for r in reversed(member.roles) if r != interaction.guild.default_role),
        None
    )

    if not current_role:
        return await interaction.response.send_message(
            f"❌ {member.mention} has no roles to promote from.", ephemeral=True
        )

    all_roles = sorted(
        [r for r in interaction.guild.roles if r != interaction.guild.default_role],
        key=lambda r: r.position
    )

    current_index = next((i for i, r in enumerate(all_roles) if r.id == current_role.id), None)

    if current_index is None:
        return await interaction.response.send_message("❌ Could not find current role in server roles.", ephemeral=True)

    next_role = None
    for r in all_roles[current_index + 1:]:
        if r.position < bot_top_role.position:
            next_role = r
            break

    if not next_role:
        return await interaction.response.send_message(
            f"❌ {member.mention} is already at the highest promotable role (`{current_role.name}`).", ephemeral=True
        )

    await member.add_roles(next_role, reason=f"Promoted by {interaction.user}")

    embed = discord.Embed(title="⬆️ Mod Promoted", color=discord.Color.green())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Old Top Role", value=current_role.mention, inline=True)
    embed.add_field(name="New Role", value=next_role.mention, inline=True)
    embed.set_footer(text=f"User ID: {member.id}")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"⬆️ {member} (`{member.id}`) promoted from **{current_role.name}** → **{next_role.name}** by {interaction.user}")

# =========================
# /checkstaff
# =========================
@tree.command(name="checkstaff", description="Analyse activity of all staff members across the server", guild=discord.Object(id=GUILD_ID))
async def checkstaff(interaction: discord.Interaction):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])

    await interaction.response.defer()

    guild = interaction.guild
    staff_role = guild.get_role(STAFF_ROLE_ID)
    if not staff_role:
        return await interaction.followup.send("❌ Staff role not found.")

    staff_members = [m for m in staff_role.members if not m.bot]
    if not staff_members:
        return await interaction.followup.send("❌ No staff members found with that role.")

    message_count: dict[int, int] = {m.id: 0 for m in staff_members}
    staff_ids = {m.id for m in staff_members}

    channels_to_scan = [guild.get_channel(cid) for cid in CHECKSTAFF_CHANNEL_IDS]
    channels_to_scan = [c for c in channels_to_scan if c is not None]

    if not channels_to_scan:
        return await interaction.followup.send("❌ Could not find the configured scan channels.")

    channel_names = ", ".join(f"#{c.name}" for c in channels_to_scan)
    status_msg = await interaction.followup.send(
        f"🔍 Scanning last **{CHECKSTAFF_SCAN_LIMIT:,}** messages in **{channel_names}** for **{len(staff_members)} staff**... this may take a while."
    )

    scanned_channels = 0
    for channel in channels_to_scan:
        try:
            async for msg in channel.history(limit=CHECKSTAFF_SCAN_LIMIT):
                if msg.author.id in staff_ids:
                    message_count[msg.author.id] += 1
            scanned_channels += 1
        except (discord.Forbidden, discord.HTTPException):
            continue

    sorted_staff = sorted(staff_members, key=lambda m: message_count[m.id], reverse=True)
    total_messages = sum(message_count.values())
    now_ts = int(datetime.now(timezone.utc).timestamp())

    overview = discord.Embed(
        title="Staff Activity Report",
        color=0x5865F2,
        timestamp=datetime.now(timezone.utc)
    )
    overview.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
    overview.set_footer(text=f"Requested by {interaction.user} • {len(staff_members)} staff scanned")
    overview.description = (
        f"**Channels:** {channel_names}\n"
        f"**Messages scanned per channel:** {CHECKSTAFF_SCAN_LIMIT:,}\n"
        f"**Total staff messages found:** {total_messages:,}\n"
        f"**Scan completed:** <t:{now_ts}:R>"
    )

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    top = sorted_staff[:5]
    top_lines = []
    for i, m in enumerate(top):
        count = message_count[m.id]
        pct = (count / total_messages * 100) if total_messages else 0
        filled = round(pct / 5)
        bar = "▰" * filled + "▱" * (20 - filled)
        top_lines.append(
            f"{medals[i]} **{m.display_name}**\n"
            f"╰ `{bar}` **{count:,}** msgs · {pct:.1f}%"
        )

    overview.add_field(
        name="── 🔥 Most Active ──",
        value="\n".join(top_lines) if top_lines else "No data",
        inline=False
    )

    bottom = sorted_staff[-5:][::-1]
    warning_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    bottom_lines = []
    for i, m in enumerate(bottom):
        count = message_count[m.id]
        pct = (count / total_messages * 100) if total_messages else 0
        bottom_lines.append(
            f"{warning_emojis[i]} **{m.display_name}** — **{count:,}** msgs · {pct:.1f}%"
        )

    overview.add_field(
        name="── 💤 Least Active ──",
        value="\n".join(bottom_lines) if bottom_lines else "No data",
        inline=False
    )

    await status_msg.edit(content=None, embed=overview)

    breakdown_lines = []
    for rank, m in enumerate(sorted_staff, 1):
        count = message_count[m.id]
        pct = (count / total_messages * 100) if total_messages else 0
        if pct >= 20:
            label = "🔴 Very High"
        elif pct >= 10:
            label = "🟠 High"
        elif pct >= 5:
            label = "🟡 Medium"
        elif count > 0:
            label = "🟢 Low"
        else:
            label = "⚫ Inactive"
        breakdown_lines.append(
            f"`#{rank:02}` **{m.display_name}** — {count:,} msgs · {pct:.1f}% · {label}"
        )

    breakdown_embeds = []
    chunk = ""
    page = 1
    for line in breakdown_lines:
        if len(chunk) + len(line) + 1 > 4000:
            e = discord.Embed(
                title=f"Full Staff Breakdown — Page {page}",
                color=0x2b2d31,
                description=chunk
            )
            e.set_footer(text=f"Page {page} • {len(staff_members)} total staff")
            breakdown_embeds.append(e)
            chunk = line + "\n"
            page += 1
        else:
            chunk += line + "\n"
    if chunk:
        e = discord.Embed(
            title="Full Staff Breakdown" + (f" — Page {page}" if page > 1 else ""),
            color=0x2b2d31,
            description=chunk
        )
        e.set_footer(text=f"{'Page ' + str(page) + ' • ' if page > 1 else ''}{len(staff_members)} total staff")
        breakdown_embeds.append(e)

    for e in breakdown_embeds:
        await interaction.followup.send(embed=e)

    await send_log(
        guild,
        f"📊 `/checkstaff` run by {interaction.user} — {len(staff_members)} staff · {total_messages:,} messages found across {scanned_channels} channel(s)"
    )

# =========================
# /autoping
# =========================
@tree.command(name="autoping", description="Repeatedly ping a member every 20 seconds with an optional message", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    action="Start or stop autoping",
    member="The member to ping",
    message="Optional custom message to include with each ping"
)
@app_commands.choices(action=[
    app_commands.Choice(name="start", value="start"),
    app_commands.Choice(name="stop", value="stop"),
])
async def autoping(interaction: discord.Interaction, action: app_commands.Choice[str], member: discord.Member = None, message: str = None):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Owner", "Authorized"])

    if action.value == "stop":
        if member:
            if member.id not in autoping_tasks:
                return await interaction.response.send_message(f"❌ No active autoping found for {member.mention}.", ephemeral=True)
            autoping_tasks[member.id].cancel()
            del autoping_tasks[member.id]
            return await interaction.response.send_message(f"⏹️ Stopped autoping for {member.mention}.", ephemeral=True)
        if not autoping_tasks:
            return await interaction.response.send_message("❌ No active autopings to stop.", ephemeral=True)
        for task in autoping_tasks.values():
            task.cancel()
        count = len(autoping_tasks)
        autoping_tasks.clear()
        return await interaction.response.send_message(f"⏹️ Stopped all {count} active autoping(s).", ephemeral=True)

    if not member:
        return await interaction.response.send_message("❌ You must specify a member to ping.", ephemeral=True)
    if member.bot:
        return await interaction.response.send_message("❌ Cannot autoping a bot.", ephemeral=True)
    if member.id in autoping_tasks:
        return await interaction.response.send_message(f"⚠️ Already autoping {member.mention}. Stop it first.", ephemeral=True)

    channel = interaction.channel
    ping_message = message or ""

    async def ping_loop():
        try:
            while True:
                content = f"{member.mention}"
                if ping_message:
                    content += f" {ping_message}"
                await channel.send(content)
                await asyncio.sleep(20)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[autoping ERROR] {e}")

    task = asyncio.create_task(ping_loop())
    autoping_tasks[member.id] = task

    embed = discord.Embed(title="📣 Autoping Started", color=discord.Color.orange())
    embed.add_field(name="Target", value=member.mention, inline=True)
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Interval", value="Every 20 seconds", inline=True)
    embed.add_field(name="Message", value=f"`{ping_message}`" if ping_message else "None", inline=False)
    embed.set_footer(text=f"Started by {interaction.user} • Use /autoping stop to end it")
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"📣 Autoping started on {member} by {interaction.user} in {channel.mention}" + (f" — Message: {ping_message}" if ping_message else ""))

# =========================
# /avatar
# =========================
@tree.command(name="avatar", description="Show a user's avatar")
@app_commands.describe(member="The member to get the avatar of (defaults to yourself)")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    av = target.display_avatar.with_size(1024)

    embed = discord.Embed(title=f"🖼️ {target.display_name}'s Avatar", color=discord.Color.blurple())
    embed.set_image(url=av.url)

    formats = []
    if av.is_animated():
        formats.append(f"[GIF]({av.replace(format='gif').url})")
    formats.append(f"[PNG]({av.replace(format='png').url})")
    formats.append(f"[JPG]({av.replace(format='jpg').url})")
    formats.append(f"[WEBP]({av.replace(format='webp').url})")
    embed.description = "  |  ".join(formats)

    if target.guild_avatar and target.guild_avatar != target.avatar:
        embed.set_footer(text="Showing server avatar • use /avatar to see global avatar")

    await interaction.response.send_message(embed=embed)

# =========================
# /banner
# =========================
@tree.command(name="banner", description="Show a user's profile banner")
@app_commands.describe(member="The member to get the banner of (defaults to yourself)")
async def banner(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    await interaction.response.defer()

    try:
        fetched = await client.fetch_user(target.id)
    except Exception:
        return await interaction.followup.send("❌ Could not fetch user data.")

    if not fetched.banner:
        return await interaction.followup.send(
            f"❌ **{target.display_name}** doesn't have a profile banner set."
        )

    banner_asset = fetched.banner.with_size(1024)

    embed = discord.Embed(title=f"🎨 {target.display_name}'s Banner", color=fetched.accent_color or discord.Color.blurple())
    embed.set_image(url=banner_asset.url)

    formats = []
    if banner_asset.is_animated():
        formats.append(f"[GIF]({banner_asset.replace(format='gif').url})")
    formats.append(f"[PNG]({banner_asset.replace(format='png').url})")
    formats.append(f"[JPG]({banner_asset.replace(format='jpg').url})")
    formats.append(f"[WEBP]({banner_asset.replace(format='webp').url})")
    embed.description = "  |  ".join(formats)

    await interaction.followup.send(embed=embed)

# =========================
# /userinfo
# =========================
@tree.command(name="userinfo", description="Show Discord info about a member")
@app_commands.describe(member="The member to look up (defaults to yourself)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user

    joined_at = int(target.joined_at.timestamp()) if hasattr(target, "joined_at") and target.joined_at else None
    created_at = int(target.created_at.timestamp())
    age_days = (datetime.now(timezone.utc) - target.created_at).days

    if interaction.guild and hasattr(target, "roles"):
        roles = [r for r in reversed(target.roles) if r != interaction.guild.default_role]
        roles_fmt = " ".join(r.mention for r in roles) if roles else "None"
        if len(roles_fmt) > 1024:
            roles_fmt = " ".join(r.mention for r in roles[:20]) + f" (+{len(roles) - 20} more)"
        top_role = target.top_role.mention if target.top_role != interaction.guild.default_role else "None"
    else:
        roles = []
        roles_fmt = "N/A (DMs)"
        top_role = "N/A (DMs)"

    badges = []
    if is_owner(target.id):
        badges.append("👑 Owner")
    if is_authorized(target.id):
        badges.append("🔐 Authorized")
    if is_blacklisted(target.id):
        badges.append("🚫 Blacklisted")
    if target.id in protected_users:
        badges.append("🛡️ Protected")
    if target.bot:
        badges.append("🤖 Bot")

    color = target.color if target.color.value != 0 else discord.Color.blurple()
    embed = discord.Embed(color=color)
    embed.set_author(name=str(target), icon_url=target.display_avatar.url)
    embed.set_thumbnail(url=target.display_avatar.url)

    embed.add_field(name="Display Name", value=target.display_name, inline=True)
    embed.add_field(name="ID", value=f"`{target.id}`", inline=True)
    embed.add_field(name="Account Age", value=f"`{age_days:,}` days", inline=True)
    embed.add_field(name="Joined Server", value=f"<t:{joined_at}:F>\n<t:{joined_at}:R>" if joined_at else "Unknown", inline=True)
    embed.add_field(name="Account Created", value=f"<t:{created_at}:F>\n<t:{created_at}:R>", inline=True)
    embed.add_field(name="Top Role", value=top_role, inline=True)
    embed.add_field(name=f"Roles ({len(roles)})", value=roles_fmt, inline=False)
    if badges:
        embed.add_field(name="Bot Flags", value="  ".join(badges), inline=False)

    embed.set_footer(text=f"Requested by {interaction.user}")
    await interaction.response.send_message(embed=embed)

# =========================
# /ship
# =========================
SHIP_BARS = ["💀", "💔", "❤️‍🔥", "💛", "💚", "💙", "💜", "🩷", "❤️", "💖", "💞"]

@tree.command(name="ship", description="Ship two random members from the server together 💘", guild=discord.Object(id=GUILD_ID))
async def ship(interaction: discord.Interaction):
    members = [m for m in interaction.guild.members if not m.bot]
    if len(members) < 2:
        return await interaction.response.send_message("❌ Not enough members to ship.", ephemeral=True)

    person1, person2 = random.sample(members, 2)
    score = random.randint(1, 100)
    filled = round(score / 10)
    bar = "█" * filled + "░" * (10 - filled)
    emoji = SHIP_BARS[min(filled, len(SHIP_BARS) - 1)]

    name1 = person1.display_name
    name2 = person2.display_name
    ship_name = name1[: max(1, len(name1) // 2)] + name2[max(0, len(name2) // 2):]

    if score <= 10:
        verdict = "Absolutely not. Run."
    elif score <= 25:
        verdict = "It's not looking good..."
    elif score <= 40:
        verdict = "There's a tiny spark, maybe."
    elif score <= 55:
        verdict = "50/50 — could go either way."
    elif score <= 70:
        verdict = "There's something there! 👀"
    elif score <= 85:
        verdict = "Strong connection! 🔥"
    elif score <= 95:
        verdict = "Almost perfect match! 💕"
    else:
        verdict = "SOULMATES. 💞"

    embed = discord.Embed(
        title=f"💘 Shipping: {name1} & {name2}",
        color=discord.Color.from_rgb(255, 105, 180)
    )
    embed.add_field(name="Ship Name", value=f"**{ship_name}**", inline=False)
    embed.add_field(name=f"Compatibility — {score}%  {emoji}", value=f"`[{bar}]`", inline=False)
    embed.add_field(name="Verdict", value=verdict, inline=False)
    embed.set_thumbnail(url=person1.display_avatar.url)
    embed.set_footer(text=f"💌 Shipped by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# =========================
# ROBLOX RANKING HELPERS
# =========================
async def get_csrf_token() -> str | None:
    try:
        async with session.post(
            "https://auth.roblox.com/v2/logout",
            cookies={".ROBLOSECURITY": ROBLOSECURITY},
            headers=headers
        ) as r:
            return r.headers.get("x-csrf-token")
    except Exception as e:
        print(f"[get_csrf_token ERROR] {e}")
        return None

async def get_group_roles(group_id: int) -> list:
    try:
        url = f"https://groups.roblox.com/v1/groups/{group_id}/roles"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            return data.get("roles", [])
    except Exception as e:
        print(f"[get_group_roles ERROR] {e}")
        return []

async def get_user_role_in_group(user_id: int, group_id: int):
    groups = await get_all_groups(user_id)
    for g in groups:
        if g["group"]["id"] == group_id:
            return g["role"]
    return None

async def set_user_rank(user_id: int, group_id: int, role_id: int) -> tuple[bool, str]:
    if not ROBLOSECURITY:
        return False, "No `.ROBLOSECURITY` cookie set in config."
    csrf = await get_csrf_token()
    if not csrf:
        return False, "Failed to fetch CSRF token from Roblox."
    try:
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        async with session.patch(
            url,
            json={"roleId": role_id},
            cookies={".ROBLOSECURITY": ROBLOSECURITY},
            headers={**headers, "X-CSRF-TOKEN": csrf, "Content-Type": "application/json"}
        ) as r:
            if r.status == 200:
                return True, "OK"
            data = await r.json()
            errors = data.get("errors", [])
            msg = errors[0].get("message", "Unknown error") if errors else f"HTTP {r.status}"
            return False, msg
    except Exception as e:
        return False, str(e)

async def exile_user(user_id: int, group_id: int) -> tuple[bool, str]:
    if not ROBLOSECURITY:
        return False, "No `.ROBLOSECURITY` cookie set in config."
    csrf = await get_csrf_token()
    if not csrf:
        return False, "Failed to fetch CSRF token from Roblox."
    try:
        url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
        async with session.delete(
            url,
            cookies={".ROBLOSECURITY": ROBLOSECURITY},
            headers={**headers, "X-CSRF-TOKEN": csrf}
        ) as r:
            if r.status == 200:
                return True, "OK"
            data = await r.json()
            errors = data.get("errors", [])
            msg = errors[0].get("message", "Unknown error") if errors else f"HTTP {r.status}"
            return False, msg
    except Exception as e:
        return False, str(e)

# =========================
# ANTINUKE HELPERS
# =========================
def _an_limit(user_id: int, key: str) -> int:
    cfg = antinuke_members.get(user_id, {})
    return cfg.get(key, ANTINUKE_DEFAULTS[key])

def _an_window(user_id: int) -> int:
    cfg = antinuke_members.get(user_id, {})
    return cfg.get("window_seconds", ANTINUKE_DEFAULTS["window_seconds"])

def _an_record(user_id: int, key: str) -> int:
    now = time.time()
    window = _an_window(user_id)
    bucket = _antinuke_counters[user_id][key]
    bucket.append(now)
    _antinuke_counters[user_id][key] = [t for t in bucket if now - t <= window]
    return len(_antinuke_counters[user_id][key])

async def _an_punish(guild: discord.Guild, member: discord.Member, reason: str):
    stripped = []
    try:
        roles_to_remove = [
            r for r in member.roles
            if r != guild.default_role
            and any(getattr(r.permissions, p, False) for p in DANGEROUS_PERMS)
            and r.position < guild.me.top_role.position
        ]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason=f"[AntiNuke] {reason}")
            stripped = [r.name for r in roles_to_remove]
    except Exception as e:
        print(f"[AntiNuke strip ERROR] {e}")

    try:
        await member.kick(reason=f"[AntiNuke] {reason}")
    except Exception as e:
        print(f"[AntiNuke kick ERROR] {e}")

    stripped_fmt = ", ".join(stripped) if stripped else "None"
    await send_log(
        guild,
        f"🛡️ **AntiNuke triggered** on {member.mention} (`{member.id}`)\n"
        f"**Reason:** {reason}\n"
        f"**Roles stripped:** {stripped_fmt}\n"
        f"**Action:** Kicked"
    )

# =========================
# ANTINUKE — GUILD EVENTS
# =========================
@client.event
async def on_guild_role_create(role: discord.Role):
    guild = role.guild
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            actor = entry.user
            break
        else:
            return
    except Exception:
        return

    if actor is None or actor.bot or actor.id not in antinuke_members:
        return
    count = _an_record(actor.id, "role_create")
    limit = _an_limit(actor.id, "role_create_limit")
    if count >= limit:
        await _an_punish(guild, guild.get_member(actor.id) or actor,
                         f"Created {count} roles within the time window (limit {limit})")

@client.event
async def on_guild_role_delete(role: discord.Role):
    guild = role.guild
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            actor = entry.user
            break
        else:
            return
    except Exception:
        return

    if actor is None or actor.bot or actor.id not in antinuke_members:
        return
    count = _an_record(actor.id, "role_delete")
    limit = _an_limit(actor.id, "role_delete_limit")
    if count >= limit:
        member = guild.get_member(actor.id)
        if member:
            await _an_punish(guild, member,
                             f"Deleted {count} roles within the time window (limit {limit})")

@client.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    guild = channel.guild
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            actor = entry.user
            break
        else:
            return
    except Exception:
        return

    if actor is None or actor.bot or actor.id not in antinuke_members:
        return
    count = _an_record(actor.id, "channel_create")
    limit = _an_limit(actor.id, "channel_create_limit")
    if count >= limit:
        member = guild.get_member(actor.id)
        if member:
            await _an_punish(guild, member,
                             f"Created {count} channels within the time window (limit {limit})")

@client.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    guild = channel.guild
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            actor = entry.user
            break
        else:
            return
    except Exception:
        return

    if actor is None or actor.bot or actor.id not in antinuke_members:
        return
    count = _an_record(actor.id, "channel_delete")
    limit = _an_limit(actor.id, "channel_delete_limit")
    if count >= limit:
        member = guild.get_member(actor.id)
        if member:
            await _an_punish(guild, member,
                             f"Deleted {count} channels within the time window (limit {limit})")

@client.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    if before.vanity_url_code == after.vanity_url_code:
        return
    guild = after
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            actor = entry.user
            break
        else:
            return
    except Exception:
        return

    if actor is None or actor.bot or actor.id not in antinuke_members:
        return
    count = _an_record(actor.id, "vanity_change")
    limit = _an_limit(actor.id, "vanity_change_limit")
    if count >= limit:
        member = guild.get_member(actor.id)
        if member:
            await _an_punish(guild, member,
                             f"Changed vanity URL (limit {limit}): `{before.vanity_url_code}` → `{after.vanity_url_code}`")

# =========================
# ANTINUKE — MESSAGE EVENTS
# =========================
INVITE_LINK_RE = re.compile(r"(discord\.gg/|discord\.com/invite/)\S+", re.IGNORECASE)

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # ---- credits: track messages for /redeemcredits ----
    message_counts[message.author.id] = message_counts.get(message.author.id, 0) + 1
    save_message_counts()

    if message.attachments and not is_owner(message.author.id):
        for attachment in message.attachments:
            matched_word = await image_contains_blacklisted_word(attachment, message.author.id)
            if matched_word:
                try:
                    await message.delete()
                except Exception:
                    pass
                try:
                    await message.channel.send(
                        f"🚫 {message.author.mention} your image was removed — it contained a blocked word (`{matched_word}`).",
                        delete_after=10
                    )
                except Exception:
                    pass
                await send_log(
                    message.guild,
                    f"🚫 **Image blacklist enforced** — deleted image from {message.author.mention} (`{message.author.id}`) containing `{matched_word}`"
                )
                return

    if message.mention_everyone and message.author.id in antinuke_members:
        count = _an_record(message.author.id, "everyone_ping")
        limit = _an_limit(message.author.id, "everyone_ping_limit")
        if count >= limit:
            member = message.guild.get_member(message.author.id)
            if member:
                try:
                    await message.delete()
                except Exception:
                    pass
                await _an_punish(message.guild, member,
                                 f"@everyone spam — {count} ping(s) (limit {limit})")
                return

    if message.author.id in antinuke_members and INVITE_LINK_RE.search(message.content):
        count = _an_record(message.author.id, "invite_spam")
        limit = _an_limit(message.author.id, "invite_spam_limit")
        if count >= limit:
            member = message.guild.get_member(message.author.id)
            if member:
                try:
                    await message.delete()
                except Exception:
                    pass
                await _an_punish(message.guild, member,
                                 f"Invite link spam — {count} link(s) in messages (limit {limit})")
                return

    content = message.content.strip()

    # ---- ,steal ----
    if content.startswith(",steal"):
        if not is_authorized(message.author.id) and not is_owner(message.author.id):
            return await message.reply("❌ You need to be authorized to use `,steal`.")

        parts = content.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.reply("❌ Usage: `,steal <emoji>`")

        raw = parts[1].strip()
        match = re.match(r"<(a?):(\w+):(\d+)>", raw)
        if not match:
            return await message.reply("❌ That doesn't look like a custom emoji. Default Discord emojis can't be stolen.")

        animated = match.group(1) == "a"
        emoji_name = match.group(2)
        emoji_id = int(match.group(3))
        ext = "gif" if animated else "png"
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=128&quality=lossless"

        try:
            async with session.get(url) as r:
                if r.status != 200:
                    return await message.reply("❌ Could not fetch the emoji image.")
                image_data = await r.read()
        except Exception as e:
            return await message.reply(f"❌ Failed to download emoji: {e}")

        try:
            new_emoji = await message.guild.create_custom_emoji(
                name=emoji_name,
                image=image_data,
                reason=f"Stolen by {message.author} via ,steal"
            )
        except discord.Forbidden:
            return await message.reply("❌ I don't have permission to add emojis in this server.")
        except discord.HTTPException as e:
            if "maximum" in str(e).lower():
                return await message.reply("❌ This server has reached the emoji limit.")
            return await message.reply(f"❌ Failed to add emoji: {e}")

        await message.reply(f"✅ Stolen and added: {new_emoji} `:{new_emoji.name}:`")
        await send_log(message.guild, f"😈 Emoji stolen by {message.author}: `:{emoji_name}:` (`{emoji_id}`)")

    # ---- ,rank ----
    elif content.startswith(",rank"):
        if not is_authorized(message.author.id) and not is_owner(message.author.id):
            return await message.reply("❌ You need to be authorized to use `,rank`.")

        parts = content.split(None, 2)
        if len(parts) < 3:
            return await message.reply("❌ Usage: `,rank <roblox username> <rank name>`")

        username, rank_query = parts[1], parts[2]
        uid = await get_user_id(username)
        if not uid:
            return await message.reply(f"❌ Roblox user `{username}` not found.")

        roles = await get_group_roles(GROUP_ID)
        if not roles:
            return await message.reply("❌ Could not fetch group roles.")

        target_role = None
        for role in roles:
            if role["name"].lower() == rank_query.lower() or str(role["rank"]) == rank_query:
                target_role = role
                break

        if not target_role:
            role_list = "\n".join(f"`{r['rank']}` — {r['name']}" for r in sorted(roles, key=lambda x: x["rank"]))
            return await message.reply(f"❌ Rank `{rank_query}` not found in the group.\n\n**Available ranks:**\n{role_list}")

        current_role = await get_user_role_in_group(uid, GROUP_ID)
        if not current_role:
            return await message.reply(f"❌ `{username}` is not in the group.")

        success, err = await set_user_rank(uid, GROUP_ID, target_role["id"])
        if not success:
            return await message.reply(f"❌ Failed to rank: {err}")

        embed = discord.Embed(title="✅ Rank Updated", color=discord.Color.green())
        embed.add_field(name="User", value=f"`{username}`", inline=True)
        embed.add_field(name="Old Rank", value=current_role["name"], inline=True)
        embed.add_field(name="New Rank", value=target_role["name"], inline=True)
        embed.set_footer(text=f"By {message.author}")
        await message.reply(embed=embed)
        await send_log(message.guild, f"📊 `{username}` ranked from **{current_role['name']}** → **{target_role['name']}** by {message.author}")

    # ---- ,promote ----
    elif content.startswith(",promote"):
        if not is_authorized(message.author.id) and not is_owner(message.author.id):
            return await message.reply("❌ You need to be authorized to use `,promote`.")

        parts = content.split(None, 1)
        if len(parts) < 2:
            return await message.reply("❌ Usage: `,promote <roblox username>`")

        username = parts[1].strip()
        uid = await get_user_id(username)
        if not uid:
            return await message.reply(f"❌ Roblox user `{username}` not found.")

        current_role = await get_user_role_in_group(uid, GROUP_ID)
        if not current_role:
            return await message.reply(f"❌ `{username}` is not in the group.")

        roles = await get_group_roles(GROUP_ID)
        if not roles:
            return await message.reply("❌ Could not fetch group roles.")

        sorted_roles = sorted(roles, key=lambda x: x["rank"])
        current_index = next((i for i, r in enumerate(sorted_roles) if r["id"] == current_role["id"]), None)

        if current_index is None:
            return await message.reply("❌ Could not find current rank in role list.")
        if current_index >= len(sorted_roles) - 1:
            return await message.reply(f"❌ `{username}` is already at the highest rank (`{current_role['name']}`).")

        next_role = sorted_roles[current_index + 1]
        success, err = await set_user_rank(uid, GROUP_ID, next_role["id"])
        if not success:
            return await message.reply(f"❌ Failed to promote: {err}")

        embed = discord.Embed(title="⬆️ Member Promoted", color=discord.Color.green())
        embed.add_field(name="User", value=f"`{username}`", inline=True)
        embed.add_field(name="Old Rank", value=current_role["name"], inline=True)
        embed.add_field(name="New Rank", value=next_role["name"], inline=True)
        embed.set_footer(text=f"By {message.author}")
        await message.reply(embed=embed)
        await send_log(message.guild, f"⬆️ `{username}` promoted from **{current_role['name']}** → **{next_role['name']}** by {message.author}")

    # ---- ,demote ----
    elif content.startswith(",demote"):
        if not is_authorized(message.author.id) and not is_owner(message.author.id):
            return await message.reply("❌ You need to be authorized to use `,demote`.")

        parts = content.split(None, 1)
        if len(parts) < 2:
            return await message.reply("❌ Usage: `,demote <roblox username>`")

        username = parts[1].strip()
        uid = await get_user_id(username)
        if not uid:
            return await message.reply(f"❌ Roblox user `{username}` not found.")

        current_role = await get_user_role_in_group(uid, GROUP_ID)
        if not current_role:
            return await message.reply(f"❌ `{username}` is not in the group.")

        roles = await get_group_roles(GROUP_ID)
        if not roles:
            return await message.reply("❌ Could not fetch group roles.")

        sorted_roles = sorted(roles, key=lambda x: x["rank"])
        current_index = next((i for i, r in enumerate(sorted_roles) if r["id"] == current_role["id"]), None)

        if current_index is None:
            return await message.reply("❌ Could not find current rank in role list.")
        if current_index <= 0:
            return await message.reply(f"❌ `{username}` is already at the lowest rank (`{current_role['name']}`).")

        prev_role = sorted_roles[current_index - 1]
        success, err = await set_user_rank(uid, GROUP_ID, prev_role["id"])
        if not success:
            return await message.reply(f"❌ Failed to demote: {err}")

        embed = discord.Embed(title="⬇️ Member Demoted", color=discord.Color.orange())
        embed.add_field(name="User", value=f"`{username}`", inline=True)
        embed.add_field(name="Old Rank", value=current_role["name"], inline=True)
        embed.add_field(name="New Rank", value=prev_role["name"], inline=True)
        embed.set_footer(text=f"By {message.author}")
        await message.reply(embed=embed)
        await send_log(message.guild, f"⬇️ `{username}` demoted from **{current_role['name']}** → **{prev_role['name']}** by {message.author}")

    # ---- ,exile ----
    elif content.startswith(",exile"):
        if not is_authorized(message.author.id) and not is_owner(message.author.id):
            return await message.reply("❌ You need to be authorized to use `,exile`.")

        parts = content.split(None, 1)
        if len(parts) < 2:
            return await message.reply("❌ Usage: `,exile <roblox username>`")

        username = parts[1].strip()
        uid = await get_user_id(username)
        if not uid:
            return await message.reply(f"❌ Roblox user `{username}` not found.")

        current_role = await get_user_role_in_group(uid, GROUP_ID)
        if not current_role:
            return await message.reply(f"❌ `{username}` is not in the group.")

        success, err = await exile_user(uid, GROUP_ID)
        if not success:
            return await message.reply(f"❌ Failed to exile: {err}")

        embed = discord.Embed(title="🚪 Member Exiled", color=discord.Color.red())
        embed.add_field(name="User", value=f"`{username}`", inline=True)
        embed.add_field(name="Was Rank", value=current_role["name"], inline=True)
        embed.set_footer(text=f"By {message.author}")
        await message.reply(embed=embed)
        await send_log(message.guild, f"🚪 `{username}` exiled from group (was **{current_role['name']}**) by {message.author}")

    # ---- ,resetrank ----
    elif content.startswith(",resetrank"):
        if not is_authorized(message.author.id) and not is_owner(message.author.id):
            return await message.reply("❌ You need to be authorized to use `,resetrank`.")

        parts = content.split(None, 1)
        if len(parts) < 2:
            return await message.reply("❌ Usage: `,resetrank <roblox username>`")

        username = parts[1].strip()
        uid = await get_user_id(username)
        if not uid:
            return await message.reply(f"❌ Roblox user `{username}` not found.")

        current_role = await get_user_role_in_group(uid, GROUP_ID)
        if not current_role:
            return await message.reply(f"❌ `{username}` is not in the group.")

        roles = await get_group_roles(GROUP_ID)
        if not roles:
            return await message.reply("❌ Could not fetch group roles.")

        member_role = next((r for r in roles if r["name"].lower() == "member"), None)
        if not member_role:
            sorted_roles = sorted([r for r in roles if r["rank"] > 0], key=lambda x: x["rank"])
            member_role = sorted_roles[0] if sorted_roles else None
        if not member_role:
            return await message.reply("❌ Could not find a Member rank in the group.")

        if current_role["id"] == member_role["id"]:
            return await message.reply(f"⚠️ `{username}` is already a **{member_role['name']}**.")

        success, err = await set_user_rank(uid, GROUP_ID, member_role["id"])
        if not success:
            return await message.reply(f"❌ Failed to reset rank: {err}")

        embed = discord.Embed(title="🔄 Rank Reset", color=discord.Color.blurple())
        embed.add_field(name="User", value=f"`{username}`", inline=True)
        embed.add_field(name="Old Rank", value=current_role["name"], inline=True)
        embed.add_field(name="Reset To", value=member_role["name"], inline=True)
        embed.set_footer(text=f"By {message.author}")
        await message.reply(embed=embed)
        await send_log(message.guild, f"🔄 `{username}` reset from **{current_role['name']}** → **{member_role['name']}** by {message.author}")

# =========================
# /rps
# =========================
RPS_CHOICES = ["🪨 Rock", "📄 Paper", "✂️ Scissors"]
RPS_BEATS = {
    "🪨 Rock": "✂️ Scissors",
    "📄 Paper": "🪨 Rock",
    "✂️ Scissors": "📄 Paper",
}
RPS_EMOJIS = {"🪨 Rock": "🪨", "📄 Paper": "📄", "✂️ Scissors": "✂️"}

class RPSView(discord.ui.View):
    def __init__(self, challenger: discord.Member):
        super().__init__(timeout=30)
        self.challenger = challenger
        self.player_choice = None
        self.finished = False

    async def resolve(self, interaction: discord.Interaction, player_choice: str):
        if interaction.user.id != self.challenger.id:
            return await interaction.response.send_message("❌ This isn't your game!", ephemeral=True)
        if self.finished:
            return
        self.finished = True
        self.stop()

        bot_choice = random.choice(RPS_CHOICES)

        if player_choice == bot_choice:
            result_text = "**It's a tie!** 🤝"
            color = discord.Color.yellow()
        elif RPS_BEATS[player_choice] == bot_choice:
            result_text = "**You win!** 🎉"
            color = discord.Color.green()
        else:
            result_text = "**You lose!** 💀"
            color = discord.Color.red()

        embed = discord.Embed(title="🪨📄✂️ Rock Paper Scissors", color=color)
        embed.add_field(name=f"{interaction.user.display_name}", value=RPS_EMOJIS[player_choice], inline=True)
        embed.add_field(name="VS", value="⚡", inline=True)
        embed.add_field(name="Bot", value=RPS_EMOJIS[bot_choice], inline=True)
        embed.add_field(name="Result", value=result_text, inline=False)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.secondary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolve(interaction, "🪨 Rock")

    @discord.ui.button(label="📄 Paper", style=discord.ButtonStyle.secondary)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolve(interaction, "📄 Paper")

    @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.secondary)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolve(interaction, "✂️ Scissors")

    async def on_timeout(self):
        self.finished = True
        for child in self.children:
            child.disabled = True

@tree.command(name="rps", description="Play rock paper scissors against the bot")
async def rps(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🪨📄✂️ Rock Paper Scissors",
        description=f"{interaction.user.mention}, make your choice!\n\nYou have **30 seconds**.",
        color=discord.Color.blurple()
    )
    view = RPSView(challenger=interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

# =========================
# CREDITS / MESSAGE SHOP COMMANDS
# =========================

@tree.command(name="redeemcredits", description="Convert your unredeemed messages into credits", guild=discord.Object(id=GUILD_ID))
async def redeemcredits(interaction: discord.Interaction):
    uid = interaction.user.id
    pending = message_counts.get(uid, 0)
    if pending <= 0:
        return await interaction.response.send_message("❌ You have no unredeemed messages to convert.", ephemeral=True)

    gained = pending * CREDITS_PER_MESSAGE
    credits[uid] = credits.get(uid, 0) + gained
    message_counts[uid] = 0
    save_credits()
    save_message_counts()

    embed = discord.Embed(title="💳 Credits Redeemed", color=0x2ecc71)
    embed.add_field(name="Messages Converted", value=f"{pending:,}", inline=True)
    embed.add_field(name="Credits Gained", value=f"{gained:,}", inline=True)
    embed.add_field(name="New Balance", value=f"{credits[uid]:,}", inline=True)
    embed.set_footer(text=f"{CREDITS_PER_MESSAGE} credits per message")
    await interaction.response.send_message(embed=embed)


@tree.command(name="addcredits", description="Manually add (or remove) credits for a member", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="Member to adjust", amount="Amount to add (use a negative number to remove)")
async def addcredits(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_authorized(interaction.user.id):
        return await deny(interaction, ["Authorized", "Owner"])

    credits[member.id] = max(0, credits.get(member.id, 0) + amount)
    save_credits()

    embed = discord.Embed(title="💳 Credits Updated", color=0x3498db)
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Change", value=f"{amount:+,}", inline=True)
    embed.add_field(name="New Balance", value=f"{credits[member.id]:,}", inline=True)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"💳 **Credits adjusted** — {interaction.user.mention} set {member.mention}'s credits by {amount:+,} (new balance: {credits[member.id]:,})")


@tree.command(name="roleroll", description="Owner only — 1% chance to win the Admin Perms role", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="Member to roll for (defaults to yourself)")
async def roleroll(interaction: discord.Interaction, member: discord.Member = None):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])

    target = member or interaction.user
    role = interaction.guild.get_role(1519321790990782484)
    if not role:
        return await interaction.response.send_message("❌ That role no longer exists on this server.", ephemeral=True)

    if role in target.roles:
        return await interaction.response.send_message(f"❌ {target.mention} already has {role.mention}.", ephemeral=True)

    won = random.random() < 0.01  # 1% chance

    if not won:
        embed = discord.Embed(title="🎲 Role Roll", description=f"{target.mention} rolled... and **lost**. Better luck next time!", color=0xe74c3c)
        return await interaction.response.send_message(embed=embed)

    try:
        await target.add_roles(role, reason=f"Won /roleroll (1% chance) — rolled by {interaction.user}")
    except Exception as e:
        return await interaction.response.send_message(f"❌ Won the roll, but failed to assign the role: {e}", ephemeral=True)

    embed = discord.Embed(title="🎲 Role Roll — JACKPOT!", description=f"{target.mention} rolled a **1% chance** and won {role.mention}! 🎉", color=0xf1c40f)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"🎲 **Roleroll jackpot** — {interaction.user.mention} rolled for {target.mention}, who won {role.mention} (1% chance)")


@tree.command(name="resetallcredits", description="Reset every member's credit balance to 0 — requires confirm:yes", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(confirm="Type yes to confirm this irreversible action")
async def resetallcredits(interaction: discord.Interaction, confirm: str):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])

    if confirm.lower() != "yes":
        return await interaction.response.send_message("❌ This resets **everyone's** credits to 0. Run again with `confirm:yes` to proceed.", ephemeral=True)

    affected = len(credits)
    credits.clear()
    save_credits()

    await interaction.response.send_message(f"✅ Reset credits for **{affected:,}** member(s) to 0.")
    await send_log(interaction.guild, f"🧹 **Credits reset** — {interaction.user.mention} reset all member credit balances ({affected:,} affected)")


creditrole_group = app_commands.Group(
    name="creditrole",
    description="View or purchase roles using credits",
)

@creditrole_group.command(name="shop", description="View the roles available to purchase with credits")
async def creditrole_shop(interaction: discord.Interaction):
    uid = interaction.user.id
    balance = credits.get(uid, 0)
    lines = []
    for tier in CREDIT_ROLE_TIERS:
        role = interaction.guild.get_role(tier["id"]) if tier["id"] else None
        role_label = role.mention if role else f"`{tier['name']}` (role not configured)"
        owned = " ✅" if role and role in interaction.user.roles else ""
        lines.append(f"{role_label} — **{tier['cost']:,}** credits{owned}")

    embed = discord.Embed(title="🛒 Credit Role Shop", description="\n".join(lines), color=0xf1c40f)
    embed.add_field(name="Your Balance", value=f"{balance:,} credits", inline=True)
    embed.add_field(name="Earning Rate", value=f"{CREDITS_PER_MESSAGE} credits / message (use `/redeemcredits`)", inline=True)
    embed.set_footer(text="Use /creditrole buy to purchase a tier")
    await interaction.response.send_message(embed=embed)


@creditrole_group.command(name="buy", description="Buy a role tier with your credits")
@app_commands.describe(tier="Which role tier to purchase")
@app_commands.choices(tier=[
    app_commands.Choice(name=t["name"], value=str(i)) for i, t in enumerate(CREDIT_ROLE_TIERS)
])
async def creditrole_buy(interaction: discord.Interaction, tier: app_commands.Choice[str]):
    idx = int(tier.value)
    info = CREDIT_ROLE_TIERS[idx]

    if not info["id"]:
        return await interaction.response.send_message("❌ This role tier hasn't been configured with a role ID yet — ask an owner to set it up.", ephemeral=True)

    role = interaction.guild.get_role(info["id"])
    if not role:
        return await interaction.response.send_message("❌ That role no longer exists on this server.", ephemeral=True)

    if role in interaction.user.roles:
        return await interaction.response.send_message(f"❌ You already have {role.mention}.", ephemeral=True)

    uid = interaction.user.id
    balance = credits.get(uid, 0)
    if balance < info["cost"]:
        return await interaction.response.send_message(
            f"❌ You need **{info['cost']:,}** credits for {role.mention}, but you only have **{balance:,}**. "
            f"Send more messages and use `/redeemcredits`.", ephemeral=True
        )

    try:
        await interaction.user.add_roles(role, reason=f"Purchased via /creditrole buy for {info['cost']} credits")
    except Exception as e:
        return await interaction.response.send_message(f"❌ Failed to assign role: {e}", ephemeral=True)

    credits[uid] = balance - info["cost"]
    save_credits()

    embed = discord.Embed(title="✅ Role Purchased", color=0x2ecc71)
    embed.add_field(name="Role", value=role.mention, inline=True)
    embed.add_field(name="Cost", value=f"{info['cost']:,} credits", inline=True)
    embed.add_field(name="Remaining Balance", value=f"{credits[uid]:,} credits", inline=True)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"🛒 **Credit role purchased** — {interaction.user.mention} bought {role.mention} for {info['cost']:,} credits (balance: {credits[uid]:,})")

tree.add_command(creditrole_group, guild=discord.Object(id=GUILD_ID))

# =========================
# /antinuke
# =========================
antinuke_group = app_commands.Group(
    name="antinuke",
    description="Manage antinuke watch on a specific member",
)

@antinuke_group.command(name="setup", description="Put a member under antinuke watch with custom limits")
@app_commands.describe(
    member="The member to watch",
    role_create_limit="Max role creates allowed (default 2)",
    role_delete_limit="Max role deletes allowed (default 2)",
    channel_create_limit="Max channel creates allowed (default 2)",
    channel_delete_limit="Max channel deletes allowed (default 2)",
    vanity_change_limit="Max vanity changes allowed (default 1 = any change kicks)",
    everyone_ping_limit="Max @everyone pings allowed (default 1)",
    invite_spam_limit="Max invite links in messages allowed (default 3)",
    window_seconds="Rolling time window in seconds (default 60)",
)
async def antinuke_setup(
    interaction: discord.Interaction,
    member: discord.Member,
    role_create_limit: int = 2,
    role_delete_limit: int = 2,
    channel_create_limit: int = 2,
    channel_delete_limit: int = 2,
    vanity_change_limit: int = 1,
    everyone_ping_limit: int = 1,
    invite_spam_limit: int = 3,
    window_seconds: int = 60,
):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if member.bot:
        return await interaction.response.send_message("❌ Cannot antinuke a bot.", ephemeral=True)
    if is_owner(member.id):
        return await interaction.response.send_message("❌ Cannot antinuke an owner.", ephemeral=True)

    antinuke_members[member.id] = {
        "username": str(member),
        "added_by": str(interaction.user),
        "added_at": datetime.now(timezone.utc).isoformat(),
        "role_create_limit": role_create_limit,
        "role_delete_limit": role_delete_limit,
        "channel_create_limit": channel_create_limit,
        "channel_delete_limit": channel_delete_limit,
        "vanity_change_limit": vanity_change_limit,
        "everyone_ping_limit": everyone_ping_limit,
        "invite_spam_limit": invite_spam_limit,
        "window_seconds": window_seconds,
    }
    save_json(ANTINUKE_FILE, {str(k): v for k, v in antinuke_members.items()})
    _antinuke_counters.pop(member.id, None)

    embed = discord.Embed(title="🛡️ AntiNuke Watch Enabled", color=discord.Color.orange())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Set By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Time Window", value=f"`{window_seconds}s`", inline=True)
    embed.add_field(name="Role Create Limit", value=f"`{role_create_limit}`", inline=True)
    embed.add_field(name="Role Delete Limit", value=f"`{role_delete_limit}`", inline=True)
    embed.add_field(name="Channel Create Limit", value=f"`{channel_create_limit}`", inline=True)
    embed.add_field(name="Channel Delete Limit", value=f"`{channel_delete_limit}`", inline=True)
    embed.add_field(name="Vanity Change Limit", value=f"`{vanity_change_limit}`", inline=True)
    embed.add_field(name="@everyone Ping Limit", value=f"`{everyone_ping_limit}`", inline=True)
    embed.add_field(name="Invite Spam Limit", value=f"`{invite_spam_limit}`", inline=True)
    embed.set_footer(text="On violation: dangerous roles stripped → member kicked")
    await interaction.response.send_message(embed=embed)
    await send_log(
        interaction.guild,
        f"🛡️ AntiNuke watch enabled on {member} (`{member.id}`) by {interaction.user}"
    )

@antinuke_group.command(name="remove", description="Remove a member from antinuke watch")
@app_commands.describe(member="The member to remove from watch")
async def antinuke_remove(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if member.id not in antinuke_members:
        return await interaction.response.send_message(
            f"⚠️ {member.mention} is not under antinuke watch.", ephemeral=True
        )
    antinuke_members.pop(member.id)
    _antinuke_counters.pop(member.id, None)
    save_json(ANTINUKE_FILE, {str(k): v for k, v in antinuke_members.items()})
    embed = discord.Embed(title="✅ AntiNuke Watch Removed", color=discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="By", value=interaction.user.mention, inline=True)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"✅ AntiNuke watch removed from {member} (`{member.id}`) by {interaction.user}")

@antinuke_group.command(name="info", description="View antinuke config and current counters for a member")
@app_commands.describe(member="The member to check")
async def antinuke_info(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if member.id not in antinuke_members:
        return await interaction.response.send_message(
            f"⚠️ {member.mention} is not under antinuke watch.", ephemeral=True
        )
    cfg = antinuke_members[member.id]
    ts = cfg.get("added_at", "Unknown")
    if ts != "Unknown":
        try:
            dt = datetime.fromisoformat(ts)
            ts = dt.strftime("%B %d, %Y at %H:%M UTC")
        except Exception:
            pass

    now = time.time()
    window = cfg.get("window_seconds", ANTINUKE_DEFAULTS["window_seconds"])
    counters = _antinuke_counters.get(member.id, {})
    def live(key):
        return len([t for t in counters.get(key, []) if now - t <= window])

    embed = discord.Embed(title="🛡️ AntiNuke Info", color=discord.Color.orange())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Added By", value=cfg.get("added_by", "Unknown"), inline=True)
    embed.add_field(name="Added At", value=ts, inline=True)
    embed.add_field(name="Time Window", value=f"`{window}s`", inline=True)
    embed.add_field(
        name="Limits (current / max)",
        value=(
            f"Role Create: `{live('role_create')}` / `{cfg.get('role_create_limit', 2)}`\n"
            f"Role Delete: `{live('role_delete')}` / `{cfg.get('role_delete_limit', 2)}`\n"
            f"Channel Create: `{live('channel_create')}` / `{cfg.get('channel_create_limit', 2)}`\n"
            f"Channel Delete: `{live('channel_delete')}` / `{cfg.get('channel_delete_limit', 2)}`\n"
            f"Vanity Change: `{live('vanity_change')}` / `{cfg.get('vanity_change_limit', 1)}`\n"
            f"@everyone Pings: `{live('everyone_ping')}` / `{cfg.get('everyone_ping_limit', 1)}`\n"
            f"Invite Links: `{live('invite_spam')}` / `{cfg.get('invite_spam_limit', 3)}`"
        ),
        inline=False,
    )
    embed.set_footer(text="Counters reset after the time window expires")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@antinuke_group.command(name="list", description="View all members currently under antinuke watch")
async def antinuke_list(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])
    if not antinuke_members:
        return await interaction.response.send_message("📭 No members are currently under antinuke watch.", ephemeral=True)

    lines = []
    for uid, cfg in antinuke_members.items():
        lines.append(f"<@{uid}> (`{uid}`) — Added by {cfg.get('added_by', 'Unknown')}")

    embed = discord.Embed(
        title="🛡️ AntiNuke Watched Members",
        description="\n".join(lines),
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Total: {len(antinuke_members)}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

tree.add_command(antinuke_group, guild=discord.Object(id=GUILD_ID))

# =========================
# /botstatus
# =========================
@tree.command(name="botstatus", description="Change the bot's activity status", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    status_type="The type of activity",
    text="The status text to display"
)
@app_commands.choices(status_type=[
    app_commands.Choice(name="Playing", value="playing"),
    app_commands.Choice(name="Watching", value="watching"),
    app_commands.Choice(name="Listening", value="listening"),
    app_commands.Choice(name="Competing", value="competing"),
    app_commands.Choice(name="Clear (remove status)", value="clear"),
])
async def botstatus(interaction: discord.Interaction, status_type: app_commands.Choice[str], text: str = None):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])

    if status_type.value == "clear":
        await client.change_presence(activity=None)
        embed = discord.Embed(title="✅ Status Cleared", color=discord.Color.green())
        embed.description = "Bot status has been removed."
        await interaction.response.send_message(embed=embed)
        await send_log(interaction.guild, f"🤖 Bot status cleared by {interaction.user}")
        return

    if not text:
        return await interaction.response.send_message("❌ You must provide a status text.", ephemeral=True)

    type_map = {
        "playing": discord.ActivityType.playing,
        "watching": discord.ActivityType.watching,
        "listening": discord.ActivityType.listening,
        "competing": discord.ActivityType.competing,
    }

    activity = discord.Activity(type=type_map[status_type.value], name=text)
    await client.change_presence(activity=activity)

    embed = discord.Embed(title="✅ Bot Status Updated", color=discord.Color.blurple())
    embed.add_field(name="Type", value=status_type.name, inline=True)
    embed.add_field(name="Text", value=text, inline=True)
    embed.add_field(name="Set By", value=interaction.user.mention, inline=True)
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild, f"🤖 Bot status set to **{status_type.name}** `{text}` by {interaction.user}")

# =========================
# /viewauthorized
# =========================
@tree.command(name="viewauthorized", description="View all currently authorized users", guild=discord.Object(id=GUILD_ID))
async def viewauthorized(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])

    if not authorized_users:
        return await interaction.response.send_message("📭 No authorized users.", ephemeral=True)

    lines = []
    for uid in authorized_users:
        member = interaction.guild.get_member(uid)
        if member:
            lines.append(f"{member.mention} (`{uid}`) — **{member.display_name}**")
        else:
            lines.append(f"<@{uid}> (`{uid}`) — *not in server*")

    embed = discord.Embed(
        title="🔐 Authorized Users",
        description="\n".join(lines),
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Total: {len(authorized_users)}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =========================
# /viewowners
# =========================
@tree.command(name="viewowners", description="View all current owners", guild=discord.Object(id=GUILD_ID))
async def viewowners(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return await deny(interaction, ["Owner"])

    lines = []
    for uid in owners:
        member = interaction.guild.get_member(uid)
        crown = "👑 Root Owner" if uid == ROOT_OWNER_ID else "👑 Owner"
        if member:
            lines.append(f"{member.mention} (`{uid}`) — **{member.display_name}** — {crown}")
        else:
            lines.append(f"<@{uid}> (`{uid}`) — *not in server* — {crown}")

    embed = discord.Embed(
        title="👑 Owners",
        description="\n".join(lines),
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Total: {len(owners)}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =========================
# /github
# =========================
@tree.command(name="github", description="Look up a GitHub user's profile")
@app_commands.describe(username="GitHub username to look up")
async def github(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        async with session.get(f"https://api.github.com/users/{username}", headers={"User-Agent": "Mozilla/5.0"}) as r:
            if r.status == 404:
                return await interaction.followup.send("❌ User not found.")
            if r.status != 200:
                return await interaction.followup.send("❌ GitHub API error.")
            data = await r.json()
    except Exception as e:
        return await interaction.followup.send(f"❌ Error: {e}")

    year = datetime.now(timezone.utc).year
    try:
        async with session.get(f"https://api.github.com/users/{username}/events/public?per_page=100", headers={"User-Agent": "Mozilla/5.0"}) as r2:
            events = await r2.json() if r2.status == 200 else []
        contributions = sum(1 for e in events if isinstance(e, dict) and str(year) in e.get("created_at", ""))
    except Exception:
        contributions = 0

    created = data.get("created_at", "")
    if created:
        try:
            dt = datetime.fromisoformat(created.rstrip("Z"))
            created = dt.strftime("%-d %B %Y") if hasattr(dt, 'day') else dt.strftime("%d %B %Y")
        except Exception:
            created = created[:10]

    name = data.get("name") or f"@{data.get('login')}"
    login = data.get("login", username)
    bio = data.get("bio") or ""
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    public_repos = data.get("public_repos", 0)
    public_gists = data.get("public_gists", 0)
    avatar = data.get("avatar_url")
    url = data.get("html_url", f"https://github.com/{login}")
    company = data.get("company") or ""
    location = data.get("location") or ""
    blog = data.get("blog") or ""

    embed = discord.Embed(color=0x24292e)
    embed.set_author(name=f"@{login}", url=url, icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    if bio:
        embed.description = bio
    embed.add_field(
        name="Stats",
        value=f"**Followers:** {followers:,} · **Following:** {following:,} · **Public Repos:** {public_repos:,} · **Public Gists:** {public_gists:,}",
        inline=False
    )
    embed.add_field(
        name="Activity",
        value=f"**Contributions ({year}):** {contributions} · **Account Created:** {created}",
        inline=False
    )
    extras = []
    if company:
        extras.append(f"🏢 {company.strip()}")
    if location:
        extras.append(f"📍 {location}")
    if blog:
        blog_url = blog if blog.startswith("http") else f"https://{blog}"
        extras.append(f"🔗 [{blog}]({blog_url})")
    if extras:
        embed.add_field(name="Info", value=" · ".join(extras), inline=False)
    embed.add_field(name="Profile", value=f"[{url}]({url})", inline=False)
    if avatar:
        embed.set_thumbnail(url=avatar)
    embed.set_footer(text="GitHub")
    await interaction.followup.send(embed=embed)

# =========================
# /youtube
# =========================
@tree.command(name="youtube", description="Look up a YouTube channel")
@app_commands.describe(channel="YouTube channel name or handle to look up")
async def youtube(interaction: discord.Interaction, channel: str):
    await interaction.response.defer()
    if not YOUTUBE_API_KEY:
        return await interaction.followup.send("❌ YouTube API key not configured. Add `YOUTUBE_API_KEY` in the bot config.")
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {"part": "snippet", "q": channel, "type": "channel", "maxResults": 1, "key": YOUTUBE_API_KEY}
        async with session.get(search_url, params=params) as r:
            data = await r.json()
        items = data.get("items", [])
        if not items:
            return await interaction.followup.send("❌ Channel not found.")
        channel_id = items[0]["snippet"]["channelId"]

        stats_url = "https://www.googleapis.com/youtube/v3/channels"
        params2 = {"part": "snippet,statistics,brandingSettings", "id": channel_id, "key": YOUTUBE_API_KEY}
        async with session.get(stats_url, params=params2) as r2:
            data2 = await r2.json()
        ch = data2["items"][0]
        snippet = ch["snippet"]
        stats = ch["statistics"]

        name = snippet.get("title", "Unknown")
        description = snippet.get("description", "")[:200] or "No description"
        subscribers = int(stats.get("subscriberCount", 0))
        views = int(stats.get("viewCount", 0))
        videos = int(stats.get("videoCount", 0))
        created = snippet.get("publishedAt", "")[:10]
        thumb = snippet.get("thumbnails", {}).get("high", {}).get("url")
        custom_url = snippet.get("customUrl", "")
        ch_url = f"https://youtube.com/{custom_url}" if custom_url else f"https://youtube.com/channel/{channel_id}"

        embed = discord.Embed(title=name, url=ch_url, color=0xFF0000)
        embed.description = description
        embed.add_field(name="Subscribers", value=f"{subscribers:,}", inline=True)
        embed.add_field(name="Total Views", value=f"{views:,}", inline=True)
        embed.add_field(name="Videos", value=f"{videos:,}", inline=True)
        embed.add_field(name="Created", value=created, inline=True)
        if thumb:
            embed.set_thumbnail(url=thumb)
        embed.set_footer(text="YouTube")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

# =========================
# /twitch
# =========================
_twitch_token: dict = {"token": None, "expires": 0}

async def get_twitch_token() -> str | None:
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        return None
    now = time.time()
    if _twitch_token["token"] and now < _twitch_token["expires"]:
        return _twitch_token["token"]
    try:
        async with session.post(
            "https://id.twitch.tv/oauth2/token",
            params={"client_id": TWITCH_CLIENT_ID, "client_secret": TWITCH_CLIENT_SECRET, "grant_type": "client_credentials"}
        ) as r:
            data = await r.json()
            _twitch_token["token"] = data["access_token"]
            _twitch_token["expires"] = now + data.get("expires_in", 3600) - 60
            return _twitch_token["token"]
    except Exception:
        return None

@tree.command(name="twitch", description="Look up a Twitch channel")
@app_commands.describe(username="Twitch username to look up")
async def twitch(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        return await interaction.followup.send("❌ Twitch API keys not configured. Add `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` in the bot config.")
    token = await get_twitch_token()
    if not token:
        return await interaction.followup.send("❌ Could not authenticate with Twitch.")
    try:
        twitch_headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"}
        async with session.get(f"https://api.twitch.tv/helix/users?login={username}", headers=twitch_headers) as r:
            data = await r.json()
        users = data.get("data", [])
        if not users:
            return await interaction.followup.send("❌ User not found.")
        user = users[0]
        uid = user["id"]

        async with session.get(f"https://api.twitch.tv/helix/channels/followers?broadcaster_id={uid}&first=1", headers=twitch_headers) as r2:
            fdata = await r2.json()
        followers = fdata.get("total", 0)

        async with session.get(f"https://api.twitch.tv/helix/streams?user_id={uid}", headers=twitch_headers) as r3:
            sdata = await r3.json()
        stream = sdata.get("data", [])
        live = len(stream) > 0

        created = user.get("created_at", "")[:10]
        desc = user.get("description", "") or "No description"
        avatar = user.get("profile_image_url")
        display = user.get("display_name", username)
        ch_url = f"https://twitch.tv/{username}"

        embed = discord.Embed(title=display, url=ch_url, color=0x9146FF)
        if live:
            s = stream[0]
            embed.add_field(name="🔴 LIVE", value=s.get("title", ""), inline=False)
            embed.add_field(name="Game", value=s.get("game_name", "Unknown"), inline=True)
            embed.add_field(name="Viewers", value=f"{s.get('viewer_count', 0):,}", inline=True)
        else:
            embed.add_field(name="Status", value="⚫ Offline", inline=True)
        embed.add_field(name="Followers", value=f"{followers:,}", inline=True)
        embed.add_field(name="Created", value=created, inline=True)
        embed.description = desc[:200]
        if avatar:
            embed.set_thumbnail(url=avatar)
        embed.set_footer(text="Twitch")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

# =========================
# /tiktok
# =========================
@tree.command(name="tiktok", description="Look up a TikTok profile link")
@app_commands.describe(username="TikTok username to look up")
async def tiktok(interaction: discord.Interaction, username: str):
    username = username.lstrip("@")
    url = f"https://www.tiktok.com/@{username}"
    embed = discord.Embed(title=f"@{username} on TikTok", url=url, color=0x010101)
    embed.description = f"[View profile on TikTok]({url})"
    embed.set_footer(text="TikTok · API not publicly available — link only")
    await interaction.response.send_message(embed=embed)

# =========================
# /twitter
# =========================
@tree.command(name="twitter", description="Look up a Twitter/X profile link")
@app_commands.describe(username="Twitter/X username to look up")
async def twitter(interaction: discord.Interaction, username: str):
    username = username.lstrip("@")
    url = f"https://x.com/{username}"
    embed = discord.Embed(title=f"@{username} on X (Twitter)", url=url, color=0x000000)
    embed.description = f"[View profile on X]({url})"
    embed.set_footer(text="X (Twitter) · API requires paid access — link only")
    await interaction.response.send_message(embed=embed)

# =========================
# /steam
# =========================
@tree.command(name="steam", description="Look up a Steam profile by username or Steam ID")
@app_commands.describe(username="Steam username or Steam64 ID")
async def steam(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    if not STEAM_API_KEY:
        return await interaction.followup.send("❌ Steam API key not configured. Add `STEAM_API_KEY` in the bot config.")
    try:
        steam_id = None
        if username.isdigit() and len(username) == 17:
            steam_id = username
        else:
            async with session.get(
                f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={username}"
            ) as r:
                data = await r.json()
            if data.get("response", {}).get("success") == 1:
                steam_id = data["response"]["steamid"]
            else:
                return await interaction.followup.send("❌ User not found.")

        async with session.get(
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steam_id}"
        ) as r2:
            pdata = await r2.json()
        players = pdata.get("response", {}).get("players", [])
        if not players:
            return await interaction.followup.send("❌ Could not fetch profile.")
        p = players[0]

        async with session.get(
            f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=false"
        ) as r3:
            gdata = await r3.json()
        game_count = gdata.get("response", {}).get("game_count", 0)

        async with session.get(
            f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={STEAM_API_KEY}&steamid={steam_id}&relationship=friend"
        ) as r4:
            fdata = await r4.json()
        friend_count = len(fdata.get("friendslist", {}).get("friends", []))

        name = p.get("personaname", "Unknown")
        avatar = p.get("avatarfull")
        profile_url = p.get("profileurl", f"https://steamcommunity.com/profiles/{steam_id}")
        real_name = p.get("realname", "")
        location = p.get("loccountrycode", "")
        state_map = {0: "⚫ Offline", 1: "🟢 Online", 2: "🟡 Busy", 3: "🟡 Away", 4: "🟡 Snooze", 5: "🟢 Looking to Trade", 6: "🟢 Looking to Play"}
        status = state_map.get(p.get("personastate", 0), "Unknown")
        current_game = p.get("gameextrainfo", "")
        created_ts = p.get("timecreated")
        created = datetime.fromtimestamp(created_ts).strftime("%d %B %Y") if created_ts else "Unknown"

        embed = discord.Embed(title=name, url=profile_url, color=0x1b2838)
        if real_name:
            embed.add_field(name="Real Name", value=real_name, inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        if current_game:
            embed.add_field(name="Currently Playing", value=current_game, inline=True)
        embed.add_field(name="Games", value=f"{game_count:,}", inline=True)
        embed.add_field(name="Friends", value=f"{friend_count:,}", inline=True)
        if location:
            embed.add_field(name="Country", value=f":flag_{location.lower()}: {location}", inline=True)
        embed.add_field(name="Account Created", value=created, inline=True)
        embed.add_field(name="Steam64 ID", value=f"`{steam_id}`", inline=True)
        if avatar:
            embed.set_thumbnail(url=avatar)
        embed.set_footer(text="Steam")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

# =========================
# RUN
# =========================
if not TOKEN:
    raise ValueError("Set your bot token in the TOKEN variable at the top of the file.")
client.run(TOKEN)

