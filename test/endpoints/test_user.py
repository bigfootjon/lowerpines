# pyre-strict
from unittest import TestCase, mock
from unittest.mock import MagicMock

from lowerpines.endpoints.user import User
from lowerpines.gmi import GMI


class TestUser(TestCase):
    @mock.patch("lowerpines.endpoints.user.UserUpdateRequest.__init__")
    def test_save(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            User(GMI("test")).save()

    @mock.patch("lowerpines.endpoints.user.UserMeRequest.__init__")
    def test_refresh(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            User(GMI("test")).refresh()

    @mock.patch("lowerpines.endpoints.user.UserMeRequest.__init__")
    def test_get(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            User.get(GMI("test"))

    @mock.patch("lowerpines.endpoints.user.SmsCreateRequest.__init__")
    def test_enable_sms(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            User(GMI("test")).enable_sms(1, "test")

    @mock.patch("lowerpines.endpoints.user.SmsDeleteRequest.__init__")
    def test_disable_sms(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            User(GMI("test")).disable_sms()
