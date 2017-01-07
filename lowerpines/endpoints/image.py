from lowerpines.endpoints.request import Request


class ImageConvertRequest(Request):
    def __init__(self, data, gmi):
        self.data = data
        super().__init__(gmi)

    def url(self):
        return 'https://image.groupme.com/pictures'

    def mode(self):
        return "POST_RAW"

    def args(self):
        return self.data

    def parse(self, response):
        return response['payload']['url']

