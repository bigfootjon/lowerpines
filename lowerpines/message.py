from lowerpines.endpoints.message import Message


class MessageManager:
    def __init__(self, gmi):
        self.gmi = gmi

    def get(self, group_id, message_id):
        return Message.get(self.gmi, group_id, message_id)


class MessageAttach:
    def __add__(self, other):
        if isinstance(other, ComplexMessage):
            other.contents.append(self)
            return other
        else:
            return ComplexMessage([self, other])

    def __radd__(self, other):
        if isinstance(other, ComplexMessage):
            other.contents.append(self)
            return other
        else:
            return ComplexMessage([other, self])


class RefAttach(MessageAttach):
    def __init__(self, user_id, display=''):
        self.display = display
        self.user_id = user_id

    def __str__(self):
        return self.display

    def __repr__(self):
        return 'R:' + self.display


class ImageAttach(MessageAttach):
    def __init__(self, image_url):
        self.image_url = image_url

    def __str__(self):
        return ''

    def __repr__(self):
        return 'I:' + str(self)


class LocationAttach(MessageAttach):
    def __init__(self, name, lat, long):
        self.name = name
        self.lat = lat
        self.long = long

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'L:' + str(self)


# This feature is not supported anymore but it still exists in the API
class SplitAttach(MessageAttach):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return self.token

    def __repr__(self):
        return 'S:' + str(self)


EMOJI_PLACEHOLDER = '\u200B'


class EmojiAttach(MessageAttach):
    def __init__(self, pack_id):
        self.pack_id = pack_id

    def __str__(self):
        return EMOJI_PLACEHOLDER

    def __repr__(self):
        return 'E:' + str(self)


class ComplexMessage:
    def __init__(self, data):
        if isinstance(data, list):
            self.contents = data
        else:
            self.contents = [data]

    def __add__(self, other):
        if isinstance(other, self.__class__):
            self.contents.extend(other.contents)
        else:
            self.contents.append(other)
        return self

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            self.contents = other.contents + self.contents
        else:
            self.contents.insert(0, other)
        return self

    def __str__(self):
        return str(self.contents)

    def get_text(self):
        return ''.join([str(part) for part in self.contents])

    def get_attachments(self):
        attach_list = []
        mentions = {
            'type': 'mentions',
            'user_ids': list(),
            'loci': list()
        }
        emojis = {
            'type': 'emoji',
            'placeholder': EMOJI_PLACEHOLDER,
            'charmap': []
        }
        content_frag = ""
        for part in self.contents:
            if isinstance(part, RefAttach):
                mentions['user_ids'].append(part.user_id)
                mentions['loci'].append([len(content_frag), len(part.display)])
                if mentions not in attach_list:
                    attach_list.append(mentions)
            elif isinstance(part, ImageAttach):
                attach_list.append({
                    'type': 'image',
                    'url': part.image_url
                })
            elif isinstance(part, LocationAttach):
                attach_list.append({
                    'type': 'location',
                    'name': part.name,
                    'lat': part.lat,
                    'long': part.long
                })
            elif isinstance(part, SplitAttach):
                attach_list.append({
                    'type': 'split',
                    'token': part.token
                })
            elif isinstance(part, EmojiAttach):
                emojis['charmap'].append([part.pack_id, len(content_frag)])
                if emojis not in attach_list:
                    attach_list.append(emojis)
            content_frag += str(part)
        return attach_list

    def just_str(self):
        return ''.join([s for s in self.contents if isinstance(s, str)])


def smart_split_complex_message(message):
    if isinstance(message, ComplexMessage):
        return message.get_text(), message.get_attachments()
    elif isinstance(message, str):
        return message, []
    else:
        raise ValueError('Message object must be a str or ComplexMessage')
