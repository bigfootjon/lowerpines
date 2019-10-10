from unittest import TestCase

from lowerpines.gmi import GMI

from lowerpines.endpoints.sms import SmsCreateRequest


class EndpointErrorHandling(TestCase):
    def test_sms_create(self):
        with self.assertRaises(ValueError):
            SmsCreateRequest(GMI("test"), duration=50, registration_id="none")
