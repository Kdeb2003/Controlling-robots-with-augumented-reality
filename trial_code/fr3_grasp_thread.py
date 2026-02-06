import logging
import time
import threading

import numpy as np
from rcs._core.common import RobotPlatform
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk

import rcs
from rcs import sim
from xr_utils import robot_pose_4x4_to_unity

# -----------------------------
# CONFIG
# -----------------------------
ROBOT_IP = "192.168.103.1"
ROBOT_INSTANCE = RobotPlatform.SIMULATION

# -----------------------------
# LOGGING
# -----------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def pose_printer(robot, stop_event: threading.Event, interval_s: float = 0.2):
    while not stop_event.is_set():
        try:
            pose = robot.get_cartesian_position()
            T = pose.pose_matrix()
            unity_pose = robot_pose_4x4_to_unity(T)
            pos = unity_pose["position"]
            rot = unity_pose["rotation"]
            print(
                f"pose | pos=({pos['x']:.3f}, {pos['y']:.3f}, {pos['z']:.3f}) "
                f"quat=({rot['x']:.3f}, {rot['y']:.3f}, {rot['z']:.3f}, {rot['w']:.3f})"
            )
        except Exception as exc:
            print(f"pose print error: {exc}")
        time.sleep(interval_s)


def main():
    context_manger: FCI | ContextManager
    if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        user = 'Abdullah'
        pw = '9cH)Wr4H5UJ"4:c'
        context_manger = FCI(Desk(ROBOT_IP, user, pw), unlock=False, lock_when_done=False)
    else:
        context_manger = ContextManager()

    with context_manger:
        robot: rcs.common.Robot
        gripper: rcs.common.Gripper

        mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
        ik = rcs.common.Pin(
            mjcf_path,
            "attachment_site_0",
            urdf=None
        )

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
                ])
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
            robot = hw.Franka(ROBOT_IP, ik)

            robot_cfg = hw.FR3Config()
            robot_cfg.tcp_offset = rcs.common.Pose(
                pose_matrix=np.array([
                    [0.707,  0.707, 0, 0],
                    [-0.707, 0.707, 0, 0],
                    [0,      0,     1, 0.15],
                    [0,      0,     0, 1],
                ])
            )
            robot_cfg.ik_solver = hw.IKSolver.rcs_ik
            robot.set_config(robot_cfg)  # type: ignore

            gripper_cfg_hw = hw.FHConfig()
            gripper_cfg_hw.epsilon_inner = gripper_cfg_hw.epsilon_outer = 0.1
            gripper_cfg_hw.speed = 0.1
            gripper_cfg_hw.force = 30
            gripper = hw.FrankaHand(ROBOT_IP, gripper_cfg_hw)
            input("the robot is going to move, press enter whenever you are ready")

        print("Initial robot cartesian position:", robot.get_cartesian_position())
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Starting Position")

        robot.move_home()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Robot is in home position")

        gripper.open()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Gripper is open")

        robot.set_cartesian_position(rcs.common.Pose(rpy_vector=[-np.pi, 0, 0], 
                                                     translation=np.array([0.5, 0.10, 0.2])))
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Robot is at pre-grasp position")

        gripper.grasp()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(1.0)
        logger.info("Gripper has grasped the object")

        stop_event = threading.Event()
        printer_thread = threading.Thread(target=pose_printer, args=(robot, stop_event), daemon=True)
        printer_thread.start()

        robot.move_home()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Robot is in home position again")

        gripper.open()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Gripper is open again")

        stop_event.set()
        printer_thread.join(timeout=1.0)

        print("Final robot cartesian position:", robot.get_cartesian_position())
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0)
        logger.info("Done all operations successfully")


if __name__ == "__main__":
    main()