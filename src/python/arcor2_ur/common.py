from dataclasses import dataclass, field
from typing import Any

import humps
from flask import request

from arcor2.data import common, object_type
from arcor2_ur.exceptions import UrGeneral


@dataclass
class CollisionSceneObject:
    model: object_type.Models
    pose: common.Pose
    metadata: dict[str, Any] = field(default_factory=dict)


def parse_collision_body() -> tuple[common.Pose, dict[str, Any]]:
    if not isinstance(request.json, dict):
        raise UrGeneral("Body should be a JSON dict containing Pose or pose and metadata.")

    body = humps.decamelize(request.json)

    if "pose" in body:
        pose = common.Pose.from_dict(body["pose"])
        metadata = body.get("metadata", {}) or {}
        return pose, metadata

    return common.Pose.from_dict(body), {}
