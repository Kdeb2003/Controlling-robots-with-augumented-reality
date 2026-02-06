"""
fr3_storage.py

Manual data collection runner for FR3.
- No server connection
- Manually set object pose values
- Logs robot state during the action

Supports: grasp or push (set ACTION).
"""

import time
from datetime import datetime

import numpy as np
import rcs
from rcs import sim
from rcs._core.common import RobotPlatform, Pose
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk
from scipy.spatial.transform import Rotation as R

from robot_state_logger import start_state_logger


# -----------------------------
# CONFIG
# -----------------------------
ROBOT_IP = "192.168.103.1"
ROBOT_INSTANCE = RobotPlatform.HARDWARE
# ROBOT_INSTANCE = RobotPlatform.SIMULATION

ACTION = "grasp"  # "grasp" or "push"
LOG_PATH = None  # auto-generated if None
LOG_HZ = 50

# Manual target inputs (ROBOT FRAME)
# OBJECT_POSITION = np.array([0.50, 0.40, 0.07], dtype=np.float64)
# OBJECT_POSITION = np.array([0.50, 0.0, 0.07], dtype=np.float64)
OBJECT_POSITION = np.array([0.50, -0.40, 0.07], dtype=np.float64)
OBJECT_ROTATION = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64)  # quat x,y,z,w

# Push settings
PUSH_AXIS = np.array([0.0, 1.0, 0.0], dtype=np.float64)
PUSH_DIST = 0.05


# -----------------------------
# Helpers
# -----------------------------

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
            pose_matrix=np.array(
                [
                    [0.707, 0.707, 0, 0],
                    [-0.707, 0.707, 0, 0],
                    [0, 0, 1, 0.15],
                    [0, 0, 0, 1],
                ],
                dtype=np.float64,
            )
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
            pose_matrix=np.array(
                [
                    [0.707, 0.707, 0, 0],
                    [-0.707, 0.707, 0, 0],
                    [0, 0, 1, 0.15],
                    [0, 0, 0, 1],
                ],
                dtype=np.float64,
            )
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


# -----------------------------
# Actions
# -----------------------------

def _run_grasp(robot, gripper, simulation):
    robot.move_home()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    gripper.open()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    rpy_fixed = np.array([-np.pi, 0.0, 0.0], dtype=np.float64)

    target_pos = OBJECT_POSITION.copy()

    target = Pose(rpy_vector=rpy_fixed, translation=target_pos)
    robot.set_cartesian_position(target)
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    gripper.grasp()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    robot.move_home()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    gripper.open()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)


def _run_push(robot, gripper, simulation):
    robot.move_home()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    gripper.grasp()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    rpy_fixed = np.array([-np.pi, 0.0, 0.0], dtype=np.float64)

    start_pos = OBJECT_POSITION.copy()
    start_pose = Pose(rpy_vector=rpy_fixed, translation=start_pos)
    robot.set_cartesian_position(start_pose)
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    end_pos = start_pos + PUSH_AXIS * float(PUSH_DIST)
    end_pose = Pose(rpy_vector=rpy_fixed, translation=end_pos)
    robot.set_cartesian_position(end_pose)
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    robot.move_home()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)

    gripper.open()
    if simulation:
        simulation.step_until_convergence()
        time.sleep(0.5)


# -----------------------------
# Main
# -----------------------------

def main():
    context = _init_robot_and_gripper()
    with context:
        robot, gripper, simulation = _create_robot_and_gripper()

        if LOG_PATH is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = f"robot_state_{ACTION}_{run_id}.csv"
        else:
            log_path = LOG_PATH

        stop_event, thread = start_state_logger(
            robot=robot,
            gripper=gripper,
            simulation=simulation,
            path=log_path,
            hz=LOG_HZ,
            mode="hardware" if ROBOT_INSTANCE == RobotPlatform.HARDWARE else "simulation",
        )

        try:
            if ACTION == "grasp":
                _run_grasp(robot, gripper, simulation)
            elif ACTION == "push":
                _run_push(robot, gripper, simulation)
            else:
                raise ValueError(f"Unknown ACTION: {ACTION}")
        finally:
            stop_event.set()
            thread.join(timeout=2.0)


if __name__ == "__main__":
    main()