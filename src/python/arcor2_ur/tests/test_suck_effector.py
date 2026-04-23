import pytest

from arcor2.data.common import Orientation, Pose, Position
from arcor2.data.object_type import Box
from arcor2_scene_data import scene_service
from arcor2_ur.object_types.ur5e import Ur5e, UrSettings
from arcor2_ur.scripts.robot_publisher import load_robot_description
from arcor2_ur.tests.conftest import Urls


@pytest.mark.timeout(60)
def test_basics(start_processes: Urls) -> None:
    # over, ze test bezi nad upravenym URDF modelom
    robot_description = load_robot_description()
    assert "suction_base_link" in robot_description
    assert "suction_cup_link" in robot_description
    assert "suction_tcp" in robot_description
    assert "tool0_to_suction_base" in robot_description
    assert "suction_base_to_cup" in robot_description
    assert "suction_cup_to_tcp" in robot_description

    scene_service.URL = start_processes.robot_url
    box = Box("UniqueBoxId", 0.1, 0.1, 0.1)
    scene_service.upsert_collision(box, Pose(Position(1, 0, 0), Orientation(0, 0, 0, 1)))
    scene_service.start()
    assert scene_service.started()

    ot = Ur5e("", "", Pose(), UrSettings(start_processes.robot_url))

    assert len(ot.robot_joints()) == 6

    # ak je tool link nastaveny na suction_tcp, toto je prakticky runtime check,
    # ze sa s tymto TCP vie realne pracovat
    pos = ot.get_end_effector_pose("")
    orig_z = pos.position.z
    pos.position.z -= 0.05
    ot.move_to_pose("", pos, 0.5)
    pos_after = ot.get_end_effector_pose("")
    assert orig_z - pos_after.position.z > 0.045

    ot.cleanup()
