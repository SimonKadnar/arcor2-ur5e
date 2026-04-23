import os
import subprocess as sp
from importlib import resources

import rclpy  # pants: no-infer-dep
from rclpy.executors import ExternalShutdownException  # pants: no-infer-dep
from rclpy.node import Node  # pants: no-infer-dep
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy  # pants: no-infer-dep
from std_msgs.msg import Bool, String  # pants: no-infer-dep
from ur_dashboard_msgs.msg import RobotMode  # pants: no-infer-dep

from arcor2_ur.topics import ROBOT_MODE_TOPIC, ROBOT_PROGRAM_RUNNING_TOPIC


def load_robot_description() -> str:
    urdf_res = resources.files("arcor2_ur").joinpath("data/urdf/ur5e.urdf")
    meshes_res = resources.files("arcor2_ur").joinpath("data/urdf/meshes")

    text = urdf_res.read_text(encoding="utf-8")

    with resources.as_file(meshes_res) as meshes_dir:
        text = text.replace(
            "package://meshes/",
            f"file://{meshes_dir.as_posix()}/",
        )

    return text


def load_robot_description_semantic() -> str:
    ur_type = os.getenv("ARCOR2_UR_TYPE", "ur5e")
    cmd = [
        "bash",
        "-lc",
        (
            "source /opt/ros/jazzy/setup.bash >/dev/null && "
            f"xacro /opt/ros/jazzy/share/ur_moveit_config/srdf/ur.srdf.xacro name:={ur_type}"
        ),
    ]
    return sp.check_output(cmd, text=True).strip()


class PublisherNode(Node):
    def __init__(self) -> None:
        super().__init__("minimal_publisher")

        qos = QoSProfile(
            depth=1,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            reliability=QoSReliabilityPolicy.RELIABLE,
        )

        self.robot_program_running_pub = self.create_publisher(Bool, ROBOT_PROGRAM_RUNNING_TOPIC, qos)
        self.robot_mode_pub = self.create_publisher(RobotMode, ROBOT_MODE_TOPIC, qos)
        self.robot_description_pub = self.create_publisher(String, "/robot_description", qos)
        self.robot_description_semantic_pub = self.create_publisher(String, "/robot_description_semantic", qos)

        self.robot_description_msg = String()
        self.robot_description_msg.data = load_robot_description()

        self.robot_description_semantic_msg = String()
        self.robot_description_semantic_msg.data = load_robot_description_semantic()

        self.timer = self.create_timer(1.0, self._republish)

    def _republish(self) -> None:
        self.robot_program_running_pub.publish(Bool(data=True))
        self.robot_mode_pub.publish(RobotMode(mode=RobotMode.RUNNING))
        self.robot_description_pub.publish(self.robot_description_msg)
        self.robot_description_semantic_pub.publish(self.robot_description_semantic_msg)


def main() -> None:
    rclpy.init()
    publisher_node = PublisherNode()

    publisher_node._republish()

    try:
        rclpy.spin(publisher_node)
    except ExternalShutdownException:
        pass
    finally:
        publisher_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
