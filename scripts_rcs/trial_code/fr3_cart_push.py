import logging

import time
import threading

import numpy as np
from rcs._core.common import RobotPlatform
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk, load_creds_franka_desk

import rcs
from rcs import sim

# -----------------------------
# CONFIG
# -----------------------------
ROBOT_IP = "192.168.103.1"
ROBOT_INSTANCE = RobotPlatform.HARDWARE
# ROBOT_INSTANCE = RobotPlatform.SIMULATION



# -----------------------------
# LOGGING
# -----------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())



def main():
    context_manger: FCI | ContextManager
    if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        # user, pw = load_creds_franka_desk()
        user='Abdullah'
        pw='9cH)Wr4H5UJ"4:c'
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
            # cfg.tcp_offset = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())
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

            # add camera to have a rendering gui
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
            camera_set = SimCameraSet(simulation, cameras)  # noqa: F841
            simulation.open_gui()

        else:
            robot = hw.Franka(ROBOT_IP, ik)

            robot_cfg = hw.FR3Config()
            # robot_cfg.tcp_offset = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())
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
            # gripper_cfg.width_limit = 0.085
            # gripper_cfg.grasp_width = 0.04
            gripper = hw.FrankaHand(ROBOT_IP, gripper_cfg_hw)
            input("the robot is going to move, press enter whenever you are ready")


        print("Initial robot cartesian position:", robot.get_cartesian_position())
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Starting Positon")

        robot.move_home()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Robot is in home position")
        print("Initial Home:", robot.get_cartesian_position())
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Starting Positon")

        gripper.grasp()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Gripper is closed")   

        robot.set_cartesian_position(rcs.common.Pose(rpy_vector=[-np.pi,0,0],translation=np.array([0.5, 0.02, 0.2])))
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Robot at target position")
        
        # Thread Function to be used here
        # start event
        # some function which uses this as target robot.get_cartesian_positiom() which is a 4x4 matrix transformed to position and orientation by XR utils
        # Also push direction will be from the side of the objects so it would be center +/- width/2 in y axis
        robot.set_cartesian_position(rcs.common.Pose(rpy_vector=[-np.pi,0,0],translation=np.array([0.5, 0.06, 0.2])))
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Robot pushed")

        gripper.grasp()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Gripper has grasped the object")

        # Thread Function to be used here
        # start event
        # some function which uses this as target robot.get_cartesian_positiom() which is a 4x4 matrix transformed to position and orientation by XR utils
        
        robot.move_home()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Robot is in home position again")

        # stop event
        gripper.open()
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(4.0) 
        logger.info("Gripper is open again")

        print("Final robot cartesian position:", robot.get_cartesian_position())
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation.step_until_convergence()
            time.sleep(2.0) 
        logger.info("Done all operations successfully")


if __name__ == "__main__":
    main()
