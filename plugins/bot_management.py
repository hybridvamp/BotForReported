import os
import secrets
import sys
import time
import urllib

import db_management
import pyrogram
import utils


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command("reboot", prefixes=["/", "!", "#", "."])
)
def CmdReboot(client: pyrogram.Client, msg: pyrogram.types.Message):
    python = sys.executable
    db_management.DB.close()
    os.execl(python, python, *sys.argv)


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command(
        "getip",
        prefixes=["/", "!", "#", "."],
    )
)
def CmdGetIP(client: pyrogram.Client, msg: pyrogram.types.Message):
    ip = urllib.request.urlopen("https://ipecho.net/plain").read().decode("utf8")
    msg.reply_text(text=ip)


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command("backup", prefixes=["/", "!", "#", "."])
)
def CmdBackup(client: pyrogram.Client, msg: pyrogram.types.Message):
    utils.SendBackup(client=client)


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command("exec", prefixes=["/", "!", "#", "."])
)
def CmdExec(client: pyrogram.Client, msg: pyrogram.types.Message):
    expression = msg.text[len(msg.command[0]) + 2 :]

    if expression:
        text = None
        try:
            text = str(exec(expression, dict(client=client, msg=msg)))
        except Exception as error:
            text = str(error)

        if text:
            if len(text) > 4096:
                file_name = f"./downloads/message_too_long_{secrets.token_hex(5)}_{time.time()}.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(text)
                msg.reply_document(document=file_name)
                os.remove(file_name)
            else:
                msg.reply_text(text=text)


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command("eval", prefixes=["/", "!", "#", "."])
)
def CmdEval(client: pyrogram.Client, msg: pyrogram.types.Message):
    expression = msg.text[len(msg.command[0]) + 2 :]

    if expression:
        text = None
        try:
            text = str(eval(expression, dict(client=client, msg=msg)))
        except Exception as error:
            text = str(error)
        if text:
            if len(text) > 4096:
                file_name = f"./downloads/message_too_long_{secrets.token_hex(5)}_{time.time()}.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(text)
                msg.reply_document(document=file_name)
                os.remove(file_name)
            else:
                msg.reply_text(text=text)


@pyrogram.Client.on_message(
    pyrogram.filters.chat(utils.config["master"])
    & pyrogram.filters.command("block", prefixes=["/", "!", "#", "."])
)
def CmdBlock(client: pyrogram.Client, msg: pyrogram.types.Message):
    users_to_block = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            users_to_block.append(msg.reply_to_message.forward_from.id)
        elif msg.reply_to_message.text.find("(#user") != -1:
            users_to_block.append(
                int(
                    msg.reply_to_message.text[
                        msg.reply_to_message.text.find("(#user")
                        + 6 : msg.reply_to_message.text.find(")")
                    ]
                )
            )
    else:
        msg.command.remove(msg.command[0])
        users_to_block = filter(utils.IsInt, msg.command)

    txt = ""
    for usr in users_to_block:
        user: db_management.Users = db_management.Users.get_or_none(id=usr)
        if user:
            user.is_blocked = True
            user.save()
            txt += f"(#user{usr.id}) {usr.first_name}\n"
            client.send_message(chat_id=usr.id, text="You have been blocked.")

    msg.reply_text(text=f"Blocked users:\n{txt}", disable_notification=False)


@pyrogram.Client.on_message(
    pyrogram.filters.chat(utils.config["master"])
    & pyrogram.filters.command("unblock", prefixes=["/", "!", "#", "."])
)
def CmdUnblock(client: pyrogram.Client, msg: pyrogram.types.Message):
    users_to_unblock = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            users_to_unblock.append(msg.reply_to_message.forward_from.id)
        elif msg.reply_to_message.text.find("(#user") != -1:
            users_to_unblock.append(
                int(
                    msg.reply_to_message.text[
                        msg.reply_to_message.text.find("(#user")
                        + 6 : msg.reply_to_message.text.find(")")
                    ]
                )
            )
    else:
        msg.command.remove(msg.command[0])
        users_to_unblock = filter(utils.IsInt, msg.command)

    txt = ""
    for usr in users_to_unblock:
        user: db_management.Users = db_management.Users.get_or_none(id=usr)
        if user:
            user.is_blocked = False
            user.save()
            txt += f"(#user{usr.id}) {usr.first_name}\n"
            client.send_message(chat_id=usr.id, text="You have been unblocked.")

    msg.reply_text(text=f"Unblocked users:\n{txt}", disable_notification=False)
