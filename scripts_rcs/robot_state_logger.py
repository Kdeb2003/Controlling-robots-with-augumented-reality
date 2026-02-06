"""
robot_state_logger.py

Lightweight robot state logger for both hardware and simulation.
Hardware mode uses robot.get_state() for velocities.
Simulation mode uses simulation.data.qvel for velocities.
"""

import csv
import time
import threading
from typing import Optional

import numpy as np


def start_state_logger(
    robot,
    gripper,
    simulation: Optional[object] = None,
    path: str = "robot_state.csv",
    hz: int = 50,
    mode: str = "simulation",  # "hardware" or "simulation"
):
    stop_event = threading.Event()

    def _get_joint_velocity():
        if mode == "hardware":
            # Hardware: use robot.get_state() if available
            try:
                state = robot.get_state()
                if hasattr(state, "dq"):
                    return np.array(state.dq, dtype=float)
            except Exception:
                return None
            return None

        # Simulation: prefer mujoco qvel
        if simulation is not None:
            try:
                return np.array(simulation.data.qvel, dtype=float)
            except Exception:
                return None
        return None

    def _logger_loop():
        dt = 1.0 / max(hz, 1)
        t0 = time.time()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "t",
                    "x",
                    "y",
                    "z",
                    "qx",
                    "qy",
                    "qz",
                    "qw",
                    "gripper_width",
                    "q",
                    "dq",
                ]
            )
            while not stop_event.is_set():
                t = time.time() - t0
                pose = robot.get_cartesian_position()
                pos = pose.translation()
                quat = pose.rotation_q()

                try:
                    grip = gripper.get_normalized_width()
                except Exception:
                    grip = None

                q = None
                if mode == "hardware":
                    try:
                        state = robot.get_state()
                        if hasattr(state, "q"):
                            q = np.array(state.q, dtype=float)
                    except Exception:
                        q = None
                elif simulation is not None:
                    try:
                        q = np.array(simulation.data.qpos, dtype=float)
                    except Exception:
                        q = None
                if q is None:
                    try:
                        q = robot.get_joint_position()
                    except Exception:
                        q = None

                dq = _get_joint_velocity()

                writer.writerow(
                    [
                        t,
                        pos[0],
                        pos[1],
                        pos[2],
                        quat[0],
                        quat[1],
                        quat[2],
                        quat[3],
                        grip,
                        q.tolist() if q is not None else None,
                        dq.tolist() if dq is not None else None,
                    ]
                )
                time.sleep(dt)

    thread = threading.Thread(target=_logger_loop, daemon=True)
    thread.start()
    return stop_event, thread
