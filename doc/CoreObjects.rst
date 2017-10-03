============
Core Objects
============

This file contains documentation for usage of the main objects of this library:

- GMI
- Bot

This file is a work in progress so the following will be added eventually:

- Chat
- Group
- Message
- User

===
GMI
===

This object is used to represent a single GroupMe user and what they are authorized to access.

It can be created through the following methods::

    from lowerpines.gmi import get_gmi, GMI

    # This function prevents multiple instantiation of the same GMI object to prevent duplication of network requests
    gmi = get_gmi('GroupMe API Token Here')

    # GMI objects can also be created manually (this method is not recommended)
    gmi = GMI('GroupMe API Token Here')

This GMI object can then be used to access various parts of the GroupMe API::

    for bot in gmi.bots:
        print(bot)

    for chat in gmi.chats:
        print(chat)

    for group in gmi.groups:
        print(group)

    # The above are each discussed further on but all 3 support filtering based on attributes
    for group in gmi.groups.filter(creator_user_id='your_user_id'):
        print(group.name) #  This will print all groups that were created by 'your_user_id'

    # There is also a helper method that filters and then selects the first element
    group = gmi.groups.get(creator_user_id='your_user_id')

The GMI object also provides access to the access token, groupme user (discussed later on), and some helper methods::

    user = gmi.user
    access_token = gmi.access_token

    gmi.refresh() #  This clears purges all information cached by the GMI object

    # All images attached to GroupMe messages must be hosted on GroupMe servers.
    # This function re-hosts an image given by a URL onto GroupMe's servers
    img_url = gmi.convert_image_url('http://an.image/url.jpg')

===
Bot
===

The Bot object represents a GroupMe bot. They can be accessed through the following methods::

    # Accessed directly from the list of bots:
    bot = gmi.bots.get(bot_id='123')

    # Accessed indirectly from a group:
    group = gmi.groups.get(name='test group')
    bot = group.bots[0]

    # Created from scratch
    bot = gmi.bots.create(group_object, bot_name, callback_url="http://optional.where.to/send/messages", avatar_url='http://optional.groupme.image/url.jpg')

Once you have access to a Bot object, you have access to the following information and methods::

    print(bot.bot_id) # GroupMe's unique ID for this bot
    print(bot.name) # User selected name
    print(bot.group_id) # GroupMe ID for the group
    print(bot.group) # Access to the group object
    print(bot.avatar_url) # URL of the avatar
    print(bot.callback_url) # URL used to notify that new messages have been posted in this group
    print(bot.dm_notification) # This seems to do nothing but its in the API

    # These properties can be updated:
    bot.name = "New Name"
    bot.save()

    # Bots can be deleted
    bot.delete()

    # Messages can be posted as the bot:
    bot.post("Hello!") #  This function accepts ComplexMessage objects


