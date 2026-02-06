import time
import numpy as np

import rcs
from rcs import sim
from rcs._core.common import RobotPlatform
from rcs._core.sim import CameraType
from rcs.camera.sim import SimCameraConfig, SimCameraSet
from rcs_fr3._core import hw
from rcs_fr3.desk import FCI, ContextManager, Desk, load_creds_franka_desk


ROBOT_IP = "192.168.103.1"
ROBOT_INSTANCE = RobotPlatform.SIMULATION  # change to HARDWARE if needed


def main():
    context_manger: FCI | ContextManager
    if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
        user, pw = load_creds_franka_desk()
        context_manger = FCI(Desk(ROBOT_IP, user, pw), unlock=False, lock_when_done=False)
    else:
        context_manger = ContextManager()

    with context_manger:
        robot: rcs.common.Robot
        gripper: rcs.common.Gripper
        simulation: sim.Sim | None = None

        mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
        ik = rcs.common.Pin(mjcf_path, "attachment_site_0", urdf=None)

        if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
            simulation = sim.Sim(rcs.scenes["fr3_empty_world"].mjb)

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
            }
            SimCameraSet(simulation, cameras)
            simulation.open_gui()
        else:
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

            input("Robot will move, press Enter when ready")

        # ---- Trial sequence ----
        robot.move_home()
        gripper.open()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # Move to a fixed pose
        target = rcs.common.Pose(
            rpy_vector=np.array([-np.pi, 0.0, 0.0]),
            translation=np.array([0.5, 0.0, 0.2]),
        )
        robot.set_cartesian_position(target)
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # Close gripper (grasp)
        gripper.grasp()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        # Return home
        robot.move_home()
        gripper.open()
        if simulation:
            simulation.step_until_convergence()
            time.sleep(0.5)

        print("Grasp trial complete.")


if __name__ == "__main__":
    main()
