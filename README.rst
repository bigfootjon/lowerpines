==================
LowerPines Project
==================

This project provides a Python wrapper around the `GroupMe <http://groupme.com>`_ v3 API.

This is very much a work-in-progress and is **not** intended to be used in production environments.

===========
Basic Usage
===========

This requires a API key from the `GroupMe developers site <http://dev.groupme.com>`_

The first step to doing anything with this library is to create a ``GMI`` object::

    from lowerpines.gmi import GMI

    gmi = GMI(api_key='API key here')

A GMI object stores a copy of the API key and serves as a context for various functions.
Current implementation will immediately download basic data about groups, bots, and user. This process can take some
time, so don't worry if instantiation of GMI objects takes a little bit of time.
GMI objects also provide common functions::

    for group in gmi.groups:
        print(group, group.name)

    for bot in gmi.bots:
        print(bot, bot.group)

    test_group = gmi.groups.get(name='Testing Group')
    test_bot = gmi.bots.filter(group_id=test_group.group_id)
    test_bot.post('Hello, world!')

GroupMe supports complex message structures, such as including GroupMe-specific emoji, pictures, etc. This information
can be utilized through ``ComplexMessage`` objects::

    from lowerpines.message import ImageAttach

    complex_message = ImageAttach('URL to GroupMe processed image here') + 'Look at my cool picture'  # This will dynamically create a ComplexMessage object
    test_bot.post(complex_message)

The various ``___Attach`` objects will automatically convert themselves into a ``ComplexMessage`` object when added to a ``str`` or to another ``MessageAttach`` object.
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
