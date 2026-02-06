# """
# fr3_cart_grasp_xr.py

# Logic-only grasp execution (no server).
# Accepts robot-frame inputs from xr_utils.parse_xr_message().
# Streams EE pose via send_fn.
# """

# import time
# import threading
# from typing import Callable

# import numpy as np
# import rcs

# from rcs import sim
# from rcs._core.common import RobotPlatform, Pose
# from rcs._core.sim import CameraType
# from rcs.camera.sim import SimCameraConfig, SimCameraSet
# from rcs_fr3._core import hw
# from rcs_fr3.desk import FCI, ContextManager, Desk, load_creds_franka_desk
# from scipy.spatial.transform import Rotation as R

# from xr_utils import robot_pose_4x4_to_unity


# # -----------------------------
# # CONFIG
# # -----------------------------
# ROBOT_IP = "192.168.103.1"
# ROBOT_INSTANCE = RobotPlatform.HARDWARE
# # ROBOT_INSTANCE = RobotPlatform.SIMULATION
# EE_STREAM_HZ = 30.0


# def _normalized_gripper_width(gripper, width_m: float) -> float:
#     try:
#         max_w = gripper.get_state().max_unnormalized_width  # type: ignore[attr-defined]
#         print(f"max{max_w}")
#         if max_w is None:
#             raise AttributeError
#     except Exception:
#         max_w = 0.08
#     return float(np.clip(width_m / max_w, 0.0, 1.0))


# def _ee_pose_stream(stop_event: threading.Event, robot, send_fn):
#     interval = 1.0 / EE_STREAM_HZ
#     while not stop_event.is_set():
#         pose = robot.get_cartesian_position()
#         T = pose.pose_matrix()
#         unity_pose = robot_pose_4x4_to_unity(T)

#         msg = {
#             "type": "EE_POSE",
#             "position": unity_pose["position"],
#             "rotation": unity_pose["rotation"],
#             "ts": time.time(),
#         }
#         if send_fn is not None:
#             send_fn(msg)
#             print(msg)

#         time.sleep(interval)


# def _init_robot_and_gripper():
#     context_manger: FCI | ContextManager
#     if ROBOT_INSTANCE == RobotPlatform.HARDWARE:
#         user='Abdullah'
#         pw='9cH)Wr4H5UJ"4:c'
#         context_manger = FCI(Desk(ROBOT_IP, user, pw), unlock=False, lock_when_done=False)
#     else:
#         context_manger = ContextManager()

#     return context_manger


# def _create_robot_and_gripper():
#     simulation = None

#     mjcf_path = rcs.scenes["fr3_empty_world"].mjcf_robot
#     ik = rcs.common.Pin(mjcf_path, "attachment_site_0", urdf=None)

#     if ROBOT_INSTANCE == RobotPlatform.SIMULATION:
#         simulation = sim.Sim(rcs.scenes["fr3_empty_world"].mjb)
#         cfg = sim.SimRobotConfig()
#         cfg.add_id("0")
#         cfg.tcp_offset = rcs.common.Pose(
#             pose_matrix=np.array([
#                 [0.707,  0.707, 0, 0],
#                 [-0.707, 0.707, 0, 0],
#                 [0,      0,     1, 0.15],
#                 [0,      0,     0, 1],
#             ])
#         )
#         robot = rcs.sim.SimRobot(simulation, ik, cfg)

#         gripper_cfg_sim = sim.SimGripperConfig()
#         gripper_cfg_sim.add_id("0")
#         gripper = sim.SimGripper(simulation, gripper_cfg_sim)

#         cameras = {
#             "default_free": sim.SimCameraConfig(
#                 identifier="",
#                 type=CameraType.default_free,
#                 resolution_width=1280,
#                 resolution_height=720,
#                 frame_rate=20,
#             ),
#         }
#         SimCameraSet(simulation, cameras)
#         simulation.open_gui()
#     else:
#         robot = hw.Franka(ROBOT_IP, ik)

#         robot_cfg = hw.FR3Config()
#         robot_cfg.tcp_offset = rcs.common.Pose(
#             pose_matrix=np.array([
#                 [0.707,  0.707, 0, 0],
#                 [-0.707, 0.707, 0, 0],
#                 [0,      0,     1, 0.15],
#                 [0,      0,     0, 1],
#             ])
#         )
#         robot_cfg.ik_solver = hw.IKSolver.rcs_ik
#         robot.set_config(robot_cfg)  # type: ignore

#         gripper_cfg_hw = hw.FHConfig()
#         gripper_cfg_hw.epsilon_inner = gripper_cfg_hw.epsilon_outer = 0.1
#         gripper_cfg_hw.speed = 0.1
#         gripper_cfg_hw.force = 30
#         gripper = hw.FrankaHand(ROBOT_IP, gripper_cfg_hw)
#         input("Robot will move, press Enter when ready")

#     return robot, gripper, simulation


# def run_fr3_cart_grasp_xr(
#     object_position: np.ndarray,
#     object_rotation: np.ndarray,
#     object_center: np.ndarray,
#     object_width: float,
#     send_fn: Callable[[dict], None] | None = None,
# ):
#     """
#     Logic-only grasp with EE streaming.

#     Inputs are already in robot frame (from xr_utils.parse_xr_message).
#     object_rotation is quaternion (x,y,z,w).
#     """

#     context_manger = _init_robot_and_gripper()
#     with context_manger:
#         robot, gripper, simulation = _create_robot_and_gripper()

#         # # Start EE stream
#         # stop_event = threading.Event()
#         # stream_thread = threading.Thread(
#         #     target=_ee_pose_stream,
#         #     args=(stop_event, robot, send_fn),
#         #     daemon=True,
#         # )
#         # stream_thread.start()

#         # ---- Sequence ----
#         robot.move_home()
#         if simulation:
#             simulation.step_until_convergence()
#             time.sleep(0.5)

#         gripper.open()
#         if simulation:
#             simulation.step_until_convergence()
#             time.sleep(0.5)

#         # Convert quat -> RPY because your workflow uses RPY
#         rpy = R.from_quat(object_rotation).as_euler("xyz", degrees=False)
#         rpy_fixed = np.array([-np.pi, 0.0, rpy[2]], dtype=np.float64)
#         target = Pose(rpy_vector=rpy_fixed, translation=object_position)
        
#         width_norm = _normalized_gripper_width(gripper, object_width)
#         if width_norm >= 1.0:
#             if send_fn is not None:
#                 send_fn({"type": "ERROR", "reason": "WIDTH_TOO_LARGE"})
#             return
        
#         robot.set_cartesian_position(target)
#         if simulation:
#             simulation.step_until_convergence()
#             time.sleep(0.5)

#         gripper.set_normalized_width(width_norm)
#         # gripper.grasp()
#         if simulation:
#             simulation.step_until_convergence()
#             time.sleep(0.5)
        
#         # Start EE stream
#         stop_event = threading.Event()
#         stream_thread = threading.Thread(
#             target=_ee_pose_stream,
#             args=(stop_event, robot, send_fn),
#             daemon=True,
#         )
#         stream_thread.start()

#         robot.move_home()
#         if simulation:
#             simulation.step_until_convergence()
#             time.sleep(0.5)

#         gripper.open()
#         if simulation:
#             simulation.step_until_convergence()
#             time.sleep(0.5)

#         # Stop EE stream
#         stop_event.set()
#         stream_thread.join()


#         if send_fn is not None:
#             send_fn({"type": "GRASP_DONE", "success": True})
