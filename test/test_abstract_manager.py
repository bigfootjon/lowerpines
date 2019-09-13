# pyre-strict

from unittest import TestCase

from typing import List, Any

from lowerpines.exceptions import NoneFoundException, MultipleFoundException

from lowerpines.manager import AbstractManager
from lowerpines.gmi import GMI


class MockManager(AbstractManager[int]):
    def _all(self) -> List[int]:
        return [0, 1, 2, 3, 4]


class MockType:
    def __init__(self, val: int) -> None:
        self.val = val


# pyre-ignore
def mm_instance(content: Any = None):
    return MockManager(GMI("access_token_here"), content)


class TestAbstractManager(TestCase):
    def setUp(self) -> None:
        self.mm = mm_instance()
        self.mt = MockType(3)
        self.cmm = mm_instance([self.mt])
        self.cmm_multiple = mm_instance([MockType(14), MockType(14)])

    def test_all_case(self) -> None:
        for i, m in enumerate(self.mm):
            self.assertEqual(i, m)

    def test_custom_case(self) -> None:
        arr = [2, 5, 12, 77]
        mm = mm_instance(arr)
        for a, m in zip(arr, mm):
            self.assertEqual(a, m)

    def test_lazy_len_call(self) -> None:
        self.assertEqual(len(self.mm), 5)

    def test_lazy_get_item_call(self) -> None:
        self.assertEqual(self.mm[3], 3)

    def test_get_item(self) -> None:
        self.assertEqual(self.cmm.get(val=3), self.mt)

    def test_get_item_none_found(self) -> None:
        with self.assertRaises(NoneFoundException):
            self.cmm.get(val=5)

    def test_get_item_multiple_found(self) -> None:
        with self.assertRaises(MultipleFoundException):
            self.cmm_multiple.get(val=14)

    def test_filter_single(self) -> None:
        self.assertEqual(self.cmm.filter(val=3)._content, [self.mt])

    def test_filter_multiple(self) -> None:
        self.assertEqual(
            self.cmm_multiple.filter(val=14)._content,
            [self.cmm_multiple[0], self.cmm_multiple[1]],
        )
