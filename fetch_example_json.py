#!/usr/bin/env python3
# pyre-ignore-all-errors

import os
import shutil

from lowerpines.endpoints.block import Block
from lowerpines.endpoints.bot import Bot

from lowerpines.endpoints.group import Group
from lowerpines.exceptions import NoneFoundException

from lowerpines.gmi import get_gmi

IMPORT_ERROR_TEXT = "To use this script create a 'test_access_token.py' file with a TEST_ACCESS_TOKEN value"

try:
    # noinspection PyUnresolvedReferences
    from test_access_token import TEST_ACCESS_TOKEN  # type: ignore
except ModuleNotFoundError:
    print(IMPORT_ERROR_TEXT)
    exit(1)
except ImportError:
    print(IMPORT_ERROR_TEXT)
    exit(1)

TEST_DATA_FOLDER = "test_data"

allow_non_deterministic = True

if __name__ == "__main__":
    gmi = get_gmi(TEST_ACCESS_TOKEN)

    gmi.write_json_to = TEST_DATA_FOLDER
    if os.path.exists(TEST_DATA_FOLDER):
        shutil.rmtree(TEST_DATA_FOLDER)

    if allow_non_deterministic:
        TEST_GROUP_NAME = "TestGroup"
        try:
            test_group = gmi.groups.get(name=TEST_GROUP_NAME)
        except NoneFoundException:
            test_group = Group(
                gmi,
                name=TEST_GROUP_NAME,
                description="Here is the description",
                image_url="https://i.groupme.com/750x700.jpeg.bda7c13e72f00b58193bd6af2114cb24c3919d1a",
            )
            test_group.save()

        TEST_BOT_NAME = "TestBot"
        try:
            test_bot = test_group.bots.get(name=TEST_BOT_NAME)
        except NoneFoundException:
            test_bot = Bot(
                gmi,
                group_id=test_group.group_id,
                name=TEST_BOT_NAME,
                callback_url="http://example.com",
                avatar_url="https://i.groupme.com/750x700.jpeg.bda7c13e72f00b58193bd6af2114cb24c3919d1a",
                dm_notification=False,
            )
            test_bot.save()

        test_bot.save()
        test_group.save()
        test_group.refresh()

        test_bot.post("BotMessage")
        test_group.post("UserMessage")
        message = test_group.messages.recent()[0]
        message.like()
        message.refresh()

        gmi.user.get().enable_sms(15, "test")
        gmi.user.get().disable_sms()
        gmi.user.get().save()

    gmi.refresh()

    gmi.user.filter()
    gmi.groups.filter()
    gmi.groups.former()
    gmi.bots.filter()
    gmi.chats.filter()

    my_user_id = gmi.user.get().user_id

    Block(gmi).get_all(my_user_id)
    Block.block(gmi, my_user_id, "6911718")
    Block.block_exists(gmi, my_user_id, "6911718")

    if allow_non_deterministic:
        test_bot.delete()
        test_group.delete()
