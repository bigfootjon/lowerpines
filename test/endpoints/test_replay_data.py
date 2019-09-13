# pyre-strict
import json
import os
from importlib import import_module
from typing import Any, Dict, List, Optional
from unittest import TestCase, mock

from lowerpines.gmi import GMI


class MockRequestsResponse:
    # pyre-ignore
    def __init__(self, response_json: Any) -> None:
        self.response_json = response_json
        self.status_code = 200
        self.content = bytes()

    # pyre-ignore
    def json(self) -> Any:
        return {"response": self.response_json}


class TestReplayAll(TestCase):
    def setUp(self) -> None:
        test_data_dir = "test_data"
        self.json_data = {}
        for file_name in os.listdir(test_data_dir):
            klass, _ = file_name.split("_")
            with open(os.path.join(test_data_dir, file_name), "r") as file_contents:
                self.json_data[klass] = json.load(file_contents)

    def test_all(self) -> None:
        for name, recorded_data in self.json_data.items():
            with self.subTest(name=name, args=recorded_data["request"]["args"]):
                self.check_file(name, recorded_data)

    def check_file(self, name: str, recorded_data: Dict[str, Any]) -> None:
        def mocked_requests_api_call(
            url: str,
            params: Dict[str, str],
            headers: List[str],
            data: Optional[str] = None,
        ) -> MockRequestsResponse:
            if data is None:
                self.assertEqual(params, recorded_data["request"]["args"])
            else:
                self.assertEqual(json.loads(data), recorded_data["request"]["args"])
            self.assertTrue(url, recorded_data["request"]["url"])
            return MockRequestsResponse(recorded_data["response"])

        name_split = name.split(".")
        module, klass_name = ".".join(name_split[:-1]), name_split[-1]
        klass = getattr(import_module(module), klass_name)
        if recorded_data["request"]["mode"] == "GET":
            patch_func = "get"
        else:
            patch_func = "post"
        with mock.patch("requests." + patch_func, side_effect=mocked_requests_api_call):
            klass(GMI("test_gmi"), **recorded_data["request"]["init"])
