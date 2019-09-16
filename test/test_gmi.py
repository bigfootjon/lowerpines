from unittest import TestCase

from lowerpines import gmi


class GMITest(TestCase):
    def test_cache(self):
        gmi1 = gmi.get_gmi("test_token")
        self.assertEqual(gmi._gmi_objects, [gmi1])
        gmi2 = gmi.get_gmi("test_token")
        self.assertEqual(gmi1, gmi2)
        self.assertEqual(len(gmi._gmi_objects), 1)

    def test_refresh(self):
        gmi_instance = gmi.get_gmi("refresh_token")
        gmi_instance.refresh()
