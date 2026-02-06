import logging
import time
import numpy as np

from rcs._core.common import RobotPlatform
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk, load_creds_franka_desk

import rcs
from rcs import sim

ROBOT_IP = "192.168.103.1"
# ROBOT_INSTANCE = RobotPlatform.HARDWARE
ROBOT_INSTANCE = RobotPlatform.SIMULATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def move_tcp_position(robot, target_translation: np.ndarray, simulation=None, sim_sleep=0.05, steps=50):
    """
    Move robot to a TCP-relative Cartesian position.
    target_translation: np.ndarray (x, y, z) in meters, relative to robot base
    """
    # TCP offset as Pose
    tcp_pose = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())

    # Target pose in base frame (translation only)
    target_pose = rcs.common.Pose(translation=target_translation) * tcp_pose

    # Set pose
    robot.set_cartesian_position(target_pose)

    # Simulation stepping for smooth motion
    if simulation is not None:
        for _ in range(steps):
            simulation.step_until_convergence()
            time.sleep(sim_sleep)

    # IK check
    ik_success = robot.get_state().ik_success
    logger.info(f"Move to target {target_translation} | IK success: {ik_success}")


def main():
    context_manager: FCI | ContextManager

    if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        user, pw = load_creds_franka_desk()
        context_manager = FCI(
            Desk(ROBOT_IP, user, pw),
            unlock=False,
            lock_when_done=False,
        )
    else:
        context_manager = ContextManager()

    with context_manager:
        robot: rcs.common.Robot
        gripper: rcs.common.Gripper
        simulation: sim.Sim | None = None

        # -----------------------------
        # SETUP (SIMULATION / HARDWARE)
        # -----------------------------
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation = sim.Sim(rcs.scenes["fr3_empty_world"].mjb)
            mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot

            ik = rcs.common.Pin(
                mjcf_path,
                "attachment_site_0",
                urdf=mjcf_path.endswith("urdf"),
            )

            cfg = sim.SimRobotConfig()
            cfg.add_id("0")
            cfg.tcp_offset = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())
            robot = rcs.sim.SimRobot(simulation, ik, cfg)

            gripper_cfg_sim = sim.SimGripperConfig()
            gripper_cfg_sim.add_id("0")
            gripper = sim.SimGripper(simulation, gripper_cfg_sim)

            cameras = {
                "default_free": SimCameraConfig(
                    identifier="",
                    type=CameraType.default_free,
                    resolution_width=1280,
                    resolution_height=720,
                    frame_rate=20,
                ),
                "wrist": SimCameraConfig(
                    identifier="wrist_0",
                    type=CameraType.fixed,
                    resolution_width=640,
                    resolution_height=480,
                    frame_rate=30,
                ),
            }
            SimCameraSet(simulation, cameras)
            simulation.open_gui()

        else:
            mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
            ik = rcs.common.Pin(
                mjcf_path,
                "attachment_site_0",
                urdf=mjcf_path.endswith("urdf"),
            )

            robot = hw.Franka(ROBOT_IP, ik)
            robot_cfg = hw.FR3Config()
            robot_cfg.tcp_offset = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())
            robot_cfg.ik_solver = hw.IKSolver.rcs_ik
            robot.set_config(robot_cfg)  # type: ignore

            gripper_cfg_hw = hw.FHConfig()
            gripper_cfg_hw.epsilon_inner = 0.1
            gripper_cfg_hw.epsilon_outer = 0.1
            gripper_cfg_hw.speed = 0.1
            gripper_cfg_hw.force = 30
            gripper = hw.FrankaHand(ROBOT_IP, gripper_cfg_hw)

        # -----------------------------
        # MOTION SEQUENCE
        # -----------------------------
        if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
            input("Robot will move to HOME position. Press Enter to continue.")

        robot.move_home()
        gripper.open()

        if simulation is not None:
            simulation.step_until_convergence()
            time.sleep(4)

        logger.info("Robot at home")

        # -----------------------------
        # TARGET POSITION (TCP translation in robot base frame)
        # -----------------------------
        # tcp_target_translation = np.array([2.8, 0, 0])
        # logger.info(f"Moving robot to TCP target: {tcp_target_translation}")
        # move_tcp_position(robot, tcp_target_translation, simulation, sim_sleep=0.05, steps=50)
        print(robot.get_cartesian_position())
        T = robot.get_cartesian_position().translation() # 4×4 numpy array
        # current_translation = T[:3, 3]
        print(f"TCP_pisitiopn is",T)

        gripper.grasp()

        if simulation is not None:
            simulation.step_until_convergence()
            time.sleep(4)

        # delta_mov = T-tcp_target_translation 
        current_pose = rcs.common.Pose(rpy_vector=np.array([-3.14, 0, 0]), translation=np.array([0.58, 0.08, 0.3]))
        # ik_success = robot.get_state().ik_success
        # logger.info(f"Move to target {current_pose} | IK success: {ik_success}")
        if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
            input("Robot will move to target position")

        robot.set_cartesian_position(current_pose)

        if simulation is not None:
            simulation.step_until_convergence()
            time.sleep(3)

     
        if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
            input("Robot will move back to HOME position. Press Enter to continue.")

        # robot.move_home()
        if simulation is not None:
            simulation.step_until_convergence()
            time.sleep(3)

        logger.info("Robot back at home, motion sequence completed")

if __name__ == "__main__":
    main()