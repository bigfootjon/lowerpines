# pyre-strict
from unittest import TestCase, mock
from unittest.mock import MagicMock

from lowerpines.endpoints.block import Block
from lowerpines.gmi import GMI


class TestBlock(TestCase):
    @mock.patch("lowerpines.endpoints.block.BlockIndexRequest.__init__")
    def test_get_all(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            Block(GMI("test")).get_all("dummy")

    @mock.patch("lowerpines.endpoints.block.BlockBetweenRequest.__init__")
    def test_block_exists(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            Block.block_exists(GMI("test"), "dummy", "other")

    @mock.patch("lowerpines.endpoints.block.BlockCreateRequest.__init__")
    def test_block(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            Block.block(GMI("test"), "dummy", "other")

    @mock.patch("lowerpines.endpoints.block.BlockUnblockRequest.__init__")
    def test_unblock(self, request_init: MagicMock) -> None:
        request_init.side_effect = ValueError("marker")
        with self.assertRaisesRegex(ValueError, "marker"):
            Block.unblock(GMI("test"), "dummy", "other")
