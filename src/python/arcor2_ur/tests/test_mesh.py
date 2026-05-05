import time
from pathlib import Path

import pytest

from arcor2.data.common import Orientation, Pose, Position
from arcor2.data.object_type import Mesh
from arcor2_scene_data import scene_service
from arcor2_storage import client as storage_client
from arcor2_ur.object_types.ur5e import Ur5e, UrSettings
from arcor2_ur.tests.conftest import Urls

MESH_PATH = Path(__file__).parent / "test_mesh_object" / "taper.stl"
MESH_ASSET_ID = "taper.stl"


@pytest.mark.timeout(321)
def test_mesh_collision_avoidance(start_processes: Urls) -> None:
    assert MESH_PATH.is_file(), f"Test mesh file does not exist: {MESH_PATH}"

    storage_client.create_asset(
        MESH_ASSET_ID, MESH_PATH.read_bytes(), description="Test mesh for UR5e collision avoidance."
    )

    scene_service.URL = start_processes.robot_url
    scene_service.start()
    assert scene_service.started()

    ot = Ur5e("", "", Pose(), UrSettings(start_processes.robot_url))
    assert len(ot.robot_joints()) == 6

    X = 0.5
    Y = 0.0
    Z = 0.3

    start_pose = Pose(Position(X, Y, Z), Orientation(1, 0, 0, 0))
    goal_pose = Pose(Position(Y, X, Z), Orientation(1, 0, 0, 0))

    ot.move_to_pose("", start_pose, 0.3, safe=False)

    mesh = Mesh("Mesh1", MESH_ASSET_ID)
    mesh_pose = Pose(Position(0.5, 0.5, 0.5), Orientation(0, 0, 0, 1))

    scene_service.upsert_collision(mesh, mesh_pose)
    assert mesh.id in scene_service.collision_ids()
    time.sleep(100)

    ot.move_to_pose("", goal_pose, 0.3, safe=True)
    reached = ot.get_end_effector_pose("")
    assert goal_pose.position.distance(reached.position) < 0.03

    scene_service.delete_all_collisions()
    ot.cleanup()
