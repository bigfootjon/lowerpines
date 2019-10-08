.. image:: https://img.shields.io/circleci/build/github/bigfootjon/lowerpines/master
    :target: https://circleci.com/gh/bigfootjon/lowerpines
.. image:: https://img.shields.io/coveralls/github/bigfootjon/lowerpines
    :target: https://coveralls.io/github/bigfootjon/lowerpines
.. image:: https://img.shields.io/pypi/pyversions/lowerpines
    :target: https://pypi.org/project/lowerpines/
.. image:: https://img.shields.io/pypi/status/lowerpines
    :target: https://pypi.org/project/lowerpines/
.. image:: https://img.shields.io/pypi/v/lowerpines
    :target: https://pypi.org/project/lowerpines/
.. image:: https://img.shields.io/pypi/l/lowerpines
    :target: https://pypi.org/project/lowerpines/

==========================================
LowerPines: GroupMe API Wrapper for Python
==========================================

This library provides a Python wrapper around the `GroupMe <http://groupme.com>`_ v3 API.

============
Installation
============

Use ``pip`` to install::

    pip3 install lowerpines

===========
Basic Usage
===========

This requires a Access Token from the `GroupMe developers site <http://dev.groupme.com>`_

The first step to doing anything with this library is to create a ``GMI`` object::

    from lowerpines.gmi import get_gmi

    gmi = get_gmi(access_token='access token here')

A GMI object stores a copy of the Access Token and serves as a context for various functions.
The ``get_gmi(access_token)`` method will get a GMI from the cache or create one if necessary.
GMI objects also provide common functions::

    for group in gmi.groups:
        print(group, group.name)

    for bot in gmi.bots:
        print(bot, bot.group)

    for chat in gmi.chats:
        print(chat, chat.other_user)

    test_group = gmi.groups.get(name='Testing Group')
    test_bot = gmi.bots.get(group_id=test_group.group_id)
    test_bot.post('Hello, world!')

GroupMe supports complex message structures, such as including GroupMe-specific emoji, pictures, etc. This information
can be utilized through ``ComplexMessage`` objects::

    from lowerpines.message import ImageAttach

    # This will dynamically create a ComplexMessage object:
    complex_message = ImageAttach('URL to GroupMe processed image here') + 'Look at my cool picture'
    test_bot.post(complex_message)

The various ``MessageAttach`` objects (such as ``ImageAttach``, ``EmojiAttach``, etc.) will automatically convert themselves into a ``ComplexMessage`` object when added to a ``str`` or to another ``MessageAttach`` object.
However, a ``MessageAttach`` object is **not** a ``ComplexMessage`` object, so the following is not allowed::

    test_bot.post(ImageAttach('URL here'))  # This will trigger an exception

The correct way to do this is to create a ``ComplexMessage`` object manually::

    from lowerpines.message import ComplexMessage

    complex_message = ComplexMessage(ImageAttach('URL here'))
    test_bot.post(complex_message)

Viewing messages for groups is also available::

    for message in test_group.messages.recent():
        print(message.text)

Each message's text is also available as a ``ComplexMessage`` object through ``message.complex_text``

Please see the `docs <doc/>`_ directory for more information.
