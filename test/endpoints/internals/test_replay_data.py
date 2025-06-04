# pyre-strict
import json
import os
from importlib import import_module
from typing import Any, Dict, List, Optional, Type
from unittest import TestCase, mock

from lowerpines.endpoints.object import AbstractObject
from lowerpines.endpoints.request import JsonType
from lowerpines.gmi import GMI


class MockRequestsResponse:
    def __init__(self, response_json: JsonType) -> None:
        self.response_json = response_json
        self.status_code = 200
        self.content: bytes = json.dumps(response_json).encode("utf-8")

    def json(self) -> JsonType:
        return {"response": self.response_json}


class TestReplayAll(TestCase):
    def setUp(self) -> None:
        test_data_dir = "test_data"
        self.json_data: Dict[str, Any] = {}
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
            instance = klass(GMI("test_gmi"), **recorded_data["request"]["init"])
            try:
                results = instance.result
            except AttributeError:
                results = None
            if isinstance(results, list):
                for result in results:
                    self.check_types(result)
            elif results is None:
                self.assertEqual(instance.parse(recorded_data["response"]), None)
            elif type(results) in [bool]:
                pass
            else:
                self.check_types(results)

    def check_types(self, klass: Type[AbstractObject]) -> None:
        annotations = getattr(klass, "__annotations__", None)
        if annotations is None:
            from annotationlib import get_annotations  # type: ignore

            annotations = get_annotations(klass)

        for key, expected in annotations.items():
            actual = type(getattr(klass, key))

            # Make sure the key we're looking at is actually a Field
            if len(list(filter(lambda k: k.name == key, klass._fields))) == 0:
                continue

            matching_types = [expected]
            # Unions need to be deconstructed
            if repr(expected).startswith("typing.Union"):
                matching_types = expected.__args__

            # typing module types don't == with their runtime equivalents, need to clean those up
            # pyre-ignore
            matching_types_cleaned: List[Type[Any]] = []
            for matching_type in matching_types:
                if repr(matching_type).startswith("typing.List"):
                    matching_types_cleaned.append(list)
                elif repr(matching_type).startswith("typing.Dict"):
                    matching_types_cleaned.append(dict)
                elif repr(matching_type).startswith("typing.Optional"):
                    matching_types_cleaned.extend(matching_type.__args__)
                else:
                    matching_types_cleaned.append(matching_type)
            self.assertTrue(
                actual in matching_types_cleaned,
                f"{klass.__class__.__name__}.{key} expected {matching_types_cleaned} but got {type(getattr(klass, key))}",
            )
