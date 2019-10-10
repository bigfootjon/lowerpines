# pyre-strict

from unittest import TestCase, mock
from unittest.mock import MagicMock

from lowerpines import gmi


class GMITest(TestCase):
    def test_cache(self) -> None:
        gmi1 = gmi.get_gmi("test_token")
        self.assertEqual(gmi._gmi_objects, [gmi1])
        gmi2 = gmi.get_gmi("test_token")
        self.assertEqual(gmi1, gmi2)
        self.assertEqual(len(gmi._gmi_objects), 1)

    def test_refresh(self) -> None:
        gmi_instance = gmi.get_gmi("refresh_token")
        gmi_instance.refresh()

    @mock.patch("lowerpines.endpoints.request.Request.__init__")
    def test_convert_image_url(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        gmi_instance = gmi.get_gmi("convert_test")
        with self.assertRaisesRegex(ValueError, "marker"):
            gmi_instance.convert_image_url("https://example.com")
