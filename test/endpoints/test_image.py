# pyre-strict
from unittest import TestCase, mock
from unittest.mock import MagicMock

from requests import Response

from lowerpines.endpoints.image import ImageConvertRequest
from lowerpines.gmi import GMI


class TestImage(TestCase):
    @mock.patch("lowerpines.endpoints.request.Request.__init__")
    def setUp(self, request_init: MagicMock) -> None:
        self.data = bytes(123)
        self.instance = ImageConvertRequest(GMI("image_test"), self.data)

    def test_url(self) -> None:
        self.assertEqual(self.instance.url(), "https://image.groupme.com/pictures")

    def test_mode(self) -> None:
        self.assertEqual(self.instance.mode(), "POST_RAW")

    def test_args(self) -> None:
        self.assertEqual(self.instance.args(), self.data)

    def test_parse(self) -> None:
        example_url = "http://example.com/image.png"
        self.assertEqual(
            self.instance.parse({"payload": {"url": example_url}}), example_url
        )

    def test_extract_response(self) -> None:
        fake_response = Response()
        fake_response.encoding = "UTF-8"
        fake_response._content = bytes(  # type: ignore
            '{"a": 1}', fake_response.encoding
        )
        self.assertEqual(self.instance.extract_response(fake_response), {"a": 1})
