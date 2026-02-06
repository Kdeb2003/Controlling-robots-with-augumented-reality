import logging
import numpy as np
from rcs._core.common import RobotPlatform
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk, load_creds_franka_desk
import time
import rcs
from rcs import sim

ROBOT_IP = "192.168.103.1"
ROBOT_INSTANCE = RobotPlatform.SIMULATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def main():
    # For Acess
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
        simulation: sim.Sim | None = None
        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation = sim.Sim(rcs.scenes["fr3_empty_world"].mjb)
            mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
            ik = rcs.common.Pin(
                mjcf_path,
                "attachment_site_0",
                urdf=None
            )
            
            cfg = sim.SimRobotConfig()
            cfg.add_id("0")
            cfg.tcp_offset = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())
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
            mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
            ik = rcs.common.Pin(
                mjcf_path,
                "attachment_site_0",
                urdf=None

            )
            robot = hw.Franka(ROBOT_IP, ik)
            robot_cfg = hw.FR3Config()
            robot_cfg.tcp_offset = rcs.common.Pose(rcs.common.FrankaHandTCPOffset())
            robot_cfg.ik_solver = hw.IKSolver.rcs_ik
            robot.set_config(robot_cfg)  # type: ignore

            gripper_cfg_hw = hw.FHConfig()
            gripper_cfg_hw.epsilon_inner = gripper_cfg_hw.epsilon_outer = 0.1
            gripper_cfg_hw.speed = 0.1
            gripper_cfg_hw.force = 30
            gripper = hw.FrankaHand(ROBOT_IP, gripper_cfg_hw)
            input("the robot is going to move, press enter whenever you are ready")
            
            
        robot.move_home()
        print(robot.get_cartesian_position)
        if simulation is not None: 
            simulation.step_until_convergence()
            time.sleep(5.0)
        logger.info("Robot is in home position, gripper is open")

        gripper.grasp()

        if simulation is not None: 
            simulation.step_until_convergence()
            time.sleep(5.0)
        logger.info("Robot is in home position, gripper is open")
        
        
        # old_pose = robot.get_cartesian_position()
        # print(f"Old Pose {old_pose}")
        # robot.set_cartesian_position(rcs.common.Pose(rpy_vector=[-np.pi,0,0],translation=np.array([0.5,0.10, 0.40])))
        # new_pose = robot.get_cartesian_position()
        # print(f"New Pose {new_pose}")
        
        # old_pose = robot.get_cartesian_position()
        # # print(f"Old Pose {old_pose}")
        # # robot.set_cartesian_position(
        # #     robot.get_cartesian_position() * rcs.common.Pose(translation=np.array([0, 0, 0.25]))  # type: ignore
        # # )
        # new_pose = robot.get_cartesian_position()
        # print(f"New Pose {new_pose}")
        # if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        #     input(
        #         "close the gripper"
        #     )

        
        # gripper.grasp()
        # if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        #     input(
        #         "open agsain"
        #     )

        
        # gripper.open()
        # robot.move_home()
        
        # old_pose = robot.get_cartesian_position()
        # print(f"Old Pose {old_pose}")
        # # robot.set_cartesian_position_ik()
            

if __name__ == '__main__':
    main()