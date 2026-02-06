"""
fr3_cart_push_xr.py

Logic-only push execution (no server).
Inputs are robot-frame values from xr_utils.parse_xr_message().

UPDATED:
- EE streaming applies a fixed offset so streamed position corresponds to object_center,
  even if robot EE is moved to a side/start pose.
"""

import time
import threading
from typing import Callable

import numpy as np
import rcs
from rcs import sim
from rcs._core.common import RobotPlatform, Pose
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk, load_creds_franka_desk
from scipy.spatial.transform import Rotation as R

from xr_utils import robot_pose_4x4_to_unity


# -----------------------------
# CONFIG
# -----------------------------
ROBOT_IP = "192.168.103.1"
ROBOT_INSTANCE = RobotPlatform.HARDWARE
# ROBOT_INSTANCE = RobotPlatform.SIMULATION
EE_STREAM_HZ = 30.0

# push settings
PUSH_AXIS = np.array([0.0, 1.0, 0.0], dtype=np.float64)  # push along +Y in robot frame
PUSH_SIDE = 1.0  # +1 = start at +Y side, -1 = start at -Y side


def _ee_pose_stream(
    stop_event: threading.Event,
    robot,
    send_fn,
    stream_offset_robot: np.ndarray | None = None,  # NEW
):
    """
    Streams EE pose, but if stream_offset_robot is provided, it will be ADDED to EE 
    translation before converting to Unity. This lets you stream "object_center-referenced" pose.
    """
    interval = 1.0 / EE_STREAM_HZ
    if stream_offset_robot is None:
        stream_offset_robot = np.zeros(3, dtype=np.float64)

    while not stop_event.is_set():
        pose = robot.get_cartesian_position()
        T = pose.pose_matrix().copy()

        # NEW: shift the translation by the offset (robot frame)
        T[:3, 3] = T[:3, 3] + stream_offset_robot

        unity_pose = robot_pose_4x4_to_unity(T)

        msg = {
            "type": "EE_POSE",
            "position": unity_pose["position"],
            "rotation": unity_pose["rotation"],
            "ts": time.time(),
        }
        if send_fn is not None:
            send_fn(msg)
            print(msg)

        time.sleep(interval)


def _init_robot_and_gripper():
    context_manger: FCI | ContextManager
    if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        user = "Abdullah"
        pw = '9cH)Wr4H5UJ"4:c'
        context_manger = FCI(Desk(ROBOT_IP, user, pw), unlock=False, lock_when_done=False)
    else:
        context_manger = ContextManager()
    return context_manger


def _create_robot_and_gripper():
    simulation = None

    mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
    ik = rcs.common.Pin(mjcf_path, "attachment_site_0", urdf=None)

    if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
        simulation = sim.Sim(rcs.scenes["fr3_empty_world"].mjb)

        cfg = sim.SimRobotConfig()
        cfg.add_id("0")
        cfg.tcp_offset = rcs.common.Pose(
            pose_matrix=np.array([
                [0.707,  0.707, 0, 0],
                [-0.707, 0.707, 0, 0],
                [0,      0,     1, 0.15],
                [0,      0,     0, 1],
            ], dtype=np.float64)
        )
        robot = rcs.sim.SimRobot(simulation, ik, cfg)

        gripper_cfg_sim = sim.SimGripperConfig()
        gripper_cfg_sim.add_id("0")
        gripper = sim.SimGripper(simulation, gripper_cfg_sim)

        cameras = {
            "default_free": sim.SimCameraConfig(
                identifier="",
                type=CameraType.default_free,
                resolution_width=1280,
                resolution_height=720,
                frame_rate=20,
            ),
        }
        SimCameraSet(simulation, cameras)
        simulation.open_gui()
    else:
        robot = hw.Franka(ROBOT_IP, ik)

        robot_cfg = hw.FR3Config()
        robot_cfg.tcp_offset = rcs.common.Pose(
            pose_matrix=np.array([
                [0.707,  0.707, 0, 0],
                [-0.707, 0.707, 0, 0],
                [0,      0,     1, 0.15],
                [0,      0,     0, 1],
            ], dtype=np.float64)
        )
        robot_cfg.ik_solver = hw.IKSolver.rcs_ik
        robot.set_config(robot_cfg)  # type: ignore

        gripper_cfg_hw = hw.FHConfig()
        gripper_cfg_hw.epsilon_inner = gripper_cfg_hw.epsilon_outer = 0.1
        gripper_cfg_hw.speed = 0.1
        gripper_cfg_hw.force = 30
        gripper = hw.FrankaHand(ROBOT_IP, gripper_cfg_hw)
        input("Robot will move, press Enter when ready")

    return robot, gripper, simulation


def run_fr3_cart_push_xr(
    object_position: np.ndarray,
    object_rotation: np.ndarray,
    object_center: np.ndarray,
    object_width: float,
    send_fn: Callable[[dict], None] | None = None,
):
    """
    Logic-only push with EE streaming.
    Inputs are robot-frame values (from xr_utils.parse_xr_message).

    We enforce roll=-pi, pitch=0, yaw from quaternion.
    """

    context_manger = _init_robot_and_gripper()
    with context_manger:
        robot, gripper, simulation = _create_robot_and_gripper()

        # ---- Sequence ----
        robot.move_home()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # close gripper for pushing
        gripper.grasp()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # compute yaw from quat, fix roll/pitch
        yaw = R.from_quat(object_rotation).as_euler("xyz", degrees=False)[2]
        rpy_fixed = np.array([-np.pi, 0.0, yaw], dtype=np.float64)

        # side-based start pose (relative to CENTER)
        half_w = float(object_width) / 2.0
        start_pos = object_center + PUSH_AXIS * (PUSH_SIDE * half_w)
        start_pose = Pose(rpy_vector=rpy_fixed, translation=start_pos)
        robot.set_cartesian_position(start_pose)
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # NEW: while streaming, undo the side offset so Quest "sees" center reference
        stream_offset_robot = -PUSH_AXIS * (PUSH_SIDE * half_w)

        # Start EE stream
        stop_event = threading.Event()
        stream_thread = threading.Thread(
            target=_ee_pose_stream,
            args=(stop_event, robot, send_fn, stream_offset_robot),
            daemon=True,
        )
        stream_thread.start()

        # push forward (towards/through center)
        push_dist = 1.5 * float(object_width)
        end_pos = start_pos - PUSH_AXIS * (PUSH_SIDE * push_dist)
        end_pose = Pose(rpy_vector=rpy_fixed, translation=end_pos)
        robot.set_cartesian_position(end_pose)
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # Stop EE stream
        stop_event.set()
        stream_thread.join()

        # return home and open
        robot.move_home()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        gripper.open()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        if send_fn is not None:
            send_fn({"type": "PUSH_DONE", "success": True})