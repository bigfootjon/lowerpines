==================================
ComplexMessage and Related Objects
==================================

This document provides full documentation for the ``ComplexMessage`` object and related ``MessageAttach`` objects.
These objects can be found in the ``lowerpines.message`` module.

==============
ComplexMessage
==============

ComplexMessage provides a way to encode text and attachments in a single object. It provides the methods ``get_text()`` and
``get_attachments()`` to access the 2 components.

ComplexMessage objects can be manually instantiated, or created dynamically::

    # Manually:
    message = ComplexMessage(['Hello, ', RefAttach('user_id_here', '@world')])

    # Dynamically:
    message = 'Hello, ' + RefAttach('user_id_here', '@world')

The ``RefAttach`` object above is explained in the MessageAttach Objects section.
Many functions can take either a raw string or a ComplexMessage object, so there is a helper function to do the hard work::

    from lowerpines.message import smart_split_complex_message

    text, attachments = smart_split_complex_message(message)
    print(text)  # prints: "Hello, @world"
    print(attachments)  # prints: "R:@world"

    # This function also handles plain str objects:
    text, attachments = smart_split_complex_message("Howdy, partner")
    print(text) # prints: "Howdy, partner"
    print(attachments) # prints: []

However, all ``post(...)`` functions in the library will recognize and properly extract data from ComplexMessage objects.
Use of the ``smart_split_complex_message(message)`` is not necessary for working with lowerpines library functions

=====================
MessageAttach Objects
=====================

MessageAttach objects are objects that can be used in ComplexMessage objects to provide extra functionality. For example,
``RefAttach`` will create a mention in the message. They can be added to each other (or added to strings) to automatically
create a ComplexMessage object.

There are several MessageAttach objects: ``RefAttach``, ``ImageAttach``, ``LocationAttach``, ``SplitAttach``, ``EmojiAttach``
Each one inherits from MessageAttach.

=========
RefAttach
=========

This is used to create a mention in a message. It requires an ``user_id`` and optionally you can pass a ``display`` parameter
to have the mention be displayed. By default, ``display`` is empty, so the mention is hidden. By convention, mentions
usually begin with an '@' symbol. For example::

    # Hidden:
    message = RefAttach('user_id_here') + 'test'

    message.get_text() == 'test'
    message.get_attachments() == RefAttach('user_id_here')

    # Displayed:
    message = RefAttach('user_id_here', '@Eddy') + ' test'

    message.get_text() == '@Eddy test'
    message.get_attachments() == [RefAttach('user_id_here', '@Eddy')]

===========
ImageAttach
===========

This is used to display an image. It takes a single parameter: ``image_url`` which should be a string containing a URL that points to a GroupMe Image Service image. It doesn't actually matter where this is inserted into the message::

    message1 = ImageAttach('image_url_here') + 'Check out my cool image!'
    message2 = 'Check out my cool image!' + ImageAttach('image_url_here')

    message1 == message2

    message1.get_text() == 'Check out my cool image!'
    message1.get_attachments() == [ImageAttach('image_url_here')]

==============
LocationAttach
==============

This is used to send a location. It takes 3 parameters: ``name``, ``lat``, and ``long``. Name should be encoded as a string, and lat/long should be encoded as ints. ``name`` will be displayed inline::

    message = 'Meet me at ' + LocationAttach('home', 22, -80)

    message.get_text() == 'Meet me at home'
    message.get_attachments() == [LocationAttach('home', 22, -80)]

===========
SplitAttach
===========

This was used to split bills, but the feature has been discontinued. These attachments still exist in the API and can occur in older messages.
It takes a single ``token`` parameter encoded as a string::

    message = 'Lets split the bill' + SplitAttach('split_token_here')

===========
EmojiAttach
===========

GroupMe has extended emoji with GroupMe specific "packs" that can be used in the app. This attachment will encode a single emoji from
their extended set. It takes a two int parameters - ``pack_id`` and ``emoji_id``, where ``pack_id`` is the ID of the pack of emojis,
and ``emoji_id`` is the ID of the emoji within the given pack. This feature depends on an invisible
character (``\ufffd`` is used by this library) being present in the message and swapping it out client-side with the Emoji given by the ``(pack_id, emoji_id)`` pair.
For example::

    message = 'Hope everyone is doing alright' + EmojiAttach(1, 1)

    message.get_text() == 'Hope everyone is doing alright\ufffd'
    message.get_attachments() == [EmojiAttach(1, 1)]

