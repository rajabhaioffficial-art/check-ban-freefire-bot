@bot.command(name="ID")
async def check_ban_command(ctx, user_id: str = None):
    lang = user_languages.get(ctx.author.id, "en")

    # Make sure user gave an ID
    if not user_id or not user_id.isdigit():
        message = {
            "en": f"{ctx.author.mention} ❌ **Invalid UID!**\n➡️ Use: `!ID 123456789`",
            "fr": f"{ctx.author.mention} ❌ **UID invalide !**\n➡️ Exemple : `!ID 123456789`"
        }
        await ctx.send(message[lang])
        return

    print(f"Command by {ctx.author} (lang={lang}, uid={user_id})")

    async with ctx.typing():
        try:
            ban_status = await check_ban(user_id)
        except Exception as e:
            await ctx.send(f"{ctx.author.mention} ⚠️ Error:\n```{str(e)}```")
            return

        # 🚨 If API gave nothing at all
        if not ban_status:
            message = {
                "en": f"{ctx.author.mention} ❌ **Could not get any response from API. Try again later.**",
                "fr": f"{ctx.author.mention} ❌ **Impossible d'obtenir une réponse de l'API.** Réessayez plus tard."
            }
            await ctx.send(message[lang])
            return

        # 🚨 If API has no "data", show raw response
        if "data" not in ban_status:
            await ctx.send(
                f"{ctx.author.mention} ⚠️ API returned unexpected format:\n```{ban_status}```"
            )
            return

        # ✅ Normal case when API gives "data"
        data = ban_status["data"]
        is_banned = int(data.get("is_banned", 0))
        period = data.get("period", "N/A")
        nickname = data.get("nickname", "N/A")
        region = data.get("region", "N/A")

        if isinstance(period, int):
            period_str = f"more than {period} months" if lang == "en" else f"plus de {period} mois"
        else:
            period_str = "unavailable" if lang == "en" else "indisponible"

        embed = discord.Embed(
            color=0xFF0000 if is_banned else 0x00FF00,
            timestamp=ctx.message.created_at
        )

        if is_banned:
            embed.title = "▌ Banned Account 🛑" if lang == "en" else "▌ Compte banni 🛑"
            embed.description = (
                f"**• {'Reason' if lang == 'en' else 'Raison'} :** "
                f"{'This account was confirmed for using cheats.' if lang == 'en' else 'Ce compte a été confirmé comme utilisant des hacks.'}\n"
                f"**• {'Suspension duration' if lang == 'en' else 'Durée de la suspension'} :** {period_str}\n"
                f"**• {'Nickname' if lang == 'en' else 'Pseudo'} :** `{nickname}`\n"
                f"**• {'Player ID' if lang == 'en' else 'ID du joueur'} :** `{user_id}`\n"
                f"**• {'Region' if lang == 'en' else 'Région'} :** `{region}`"
            )
            file = discord.File("assets/banned.gif", filename="banned.gif")
            embed.set_image(url="attachment://banned.gif")
        else:
            embed.title = "▌ Clean Account ✅" if lang == "en" else "▌ Compte non banni ✅"
            embed.description = (
                f"**• {'Status' if lang == 'en' else 'Statut'} :** "
                f"{'No sufficient evidence of cheat usage.' if lang == 'en' else 'Aucune preuve suffisante de hacks.'}\n"
                f"**• {'Nickname' if lang == 'en' else 'Pseudo'} :** `{nickname}`\n"
                f"**• {'Player ID' if lang == 'en' else 'ID du joueur'} :** `{user_id}`\n"
                f"**• {'Region' if lang == 'en' else 'Région'} :** `{region}`"
            )
            file = discord.File("assets/notbanned.gif", filename="notbanned.gif")
            embed.set_image(url="attachment://notbanned.gif")

        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="DEVELOPED BY THUG•")

        await ctx.send(f"{ctx.author.mention}", embed=embed, file=file)
