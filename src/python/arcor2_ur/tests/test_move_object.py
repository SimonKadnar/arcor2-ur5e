import time

import pytest

from arcor2.data.common import Orientation, Pose, Position
from arcor2.data.object_type import Box
from arcor2_object_types.abstract import EffectorType, GraspableState, GraspPosition
from arcor2_scene_data import scene_service
from arcor2_ur.object_types.ur5e import Ur5e, UrSettings
from arcor2_ur.tests.conftest import Urls


# TODO: add asserts
@pytest.mark.timeout(321)
def test_move_object(start_processes: Urls) -> None:
    scene_service.URL = start_processes.robot_url
    scene_service.start()
    assert scene_service.started()

    ot = Ur5e("", "", Pose(), UrSettings(start_processes.robot_url))
    assert len(ot.robot_joints()) == 6

    box = Box("Box1", 0.1, 0.1, 0.2)
    scene_service.upsert_graspable(box, Pose(Position(0, 0.5, 0.1), Orientation(0, 0, 0, 1)), GraspableState.WORLD)
    time.sleep(1)

    ot.pick_up_object(Position(0, 0.5, 0.1), 0.5, EffectorType.SUCK, [GraspPosition.TOP])

    ot.place_object(Pose(Position(0, -0.5, 0.1), Orientation(0, 0, 0, 1)))

    scene_service.delete_all_collisions()
    ot.cleanup()
