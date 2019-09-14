# pyre-check
import hashlib
import inspect
import json
import os

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.endpoints.request import Request


def dump_json(json_dump_dir: str, req: "Request", response: Any) -> None:
    hasher = hashlib.sha1()

    def hash_user_keys(key: str, value: str) -> str:
        if key in [
            "email",
            "phone_number",
            "name",
            "user_id, zip_code",
            "image_url",
            "avatar_url",
            "group_name",
            "text",
            "nickname",
            "share_url",
            "share_qr_code_url",
        ]:
            hasher.update(value.encode("utf-8"))
            if key == "image_url":
                return "https://i.groupme.com/750x700.jpeg." + hasher.hexdigest()
            else:
                return hasher.hexdigest()
        return value

    def recursive_descend(tree: Any) -> Any:
        new_tree = {}
        if isinstance(tree, dict):
            for key, value in tree.items():
                if isinstance(value, str):
                    new_tree[key] = hash_user_keys(key, value)
                elif key.startswith("SKIP_HASH_"):
                    new_tree[key[10:]] = value
                else:
                    new_tree[key] = recursive_descend(value)
        elif isinstance(tree, list):
            new_tree = [recursive_descend(t) for t in tree]  # type: ignore
        else:
            new_tree = tree
        return new_tree

    hasher.update(json.dumps(req.args()).encode("utf-8"))
    file_name = (
        req.__class__.__module__
        + "."
        + req.__class__.__name__
        + "_"
        + hasher.hexdigest()
        + ".json"
    )
    init_args = {}
    for name in inspect.getfullargspec(req.__class__.__init__).args:
        if name in ["self", "gmi"]:
            continue
        init_args[name] = getattr(req, name)
    file_contents = {
        "request": {
            "mode": req.mode(),
            "url": req.url(),
            "SKIP_HASH_args": req.args(),
            "SKIP_HASH_init": init_args,
        },
        "response": response,
    }
    if not os.path.exists(json_dump_dir):
        os.makedirs(json_dump_dir)
    with open(os.path.join(json_dump_dir, file_name), "w") as f:
        f.write(json.dumps(recursive_descend(file_contents), indent=4, sort_keys=True))
