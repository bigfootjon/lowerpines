#!/usr/bin/env python3
# pyre-ignore-all-errors

import os
import shutil

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

if __name__ == "__main__":
    gmi = get_gmi(TEST_ACCESS_TOKEN)

    gmi.write_json_to = TEST_DATA_FOLDER
    if os.path.exists(TEST_DATA_FOLDER):
        shutil.rmtree(TEST_DATA_FOLDER)

    TEST_GROUP_NAME = "TestGroup"
    try:
        test_group = gmi.groups.get(name=TEST_GROUP_NAME)
    except NoneFoundException:
        test_group = Group(gmi, name=TEST_GROUP_NAME)
        test_group.save()

    TEST_BOT_NAME = "TestBot"
    try:
        test_bot = test_group.bots.get(name=TEST_BOT_NAME)
    except NoneFoundException:
        test_bot = Bot(gmi, group_id=test_group.group_id, name=TEST_BOT_NAME)
        test_bot.save()

    test_bot.post("BotMessage")
    test_group.post("UserMessage")
    test_group.messages.recent()

    gmi.refresh()

    gmi.user.filter()
    gmi.groups.filter()
    gmi.bots.filter()
    gmi.chats.filter()

    test_bot.delete()
    test_group.delete()
