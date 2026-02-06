"""
fr3_cart_grasp.py

Minimal skeleton for Cartesian grasp execution on FR3
with FAKE EE pose streaming.
"""

from typing import Callable
import numpy as np
import time
import threading


# =========================
# Fake EE pose streaming
# =========================

def _fake_ee_pose_stream(stop_event: threading.Event, send_fn):
    """
    Fake end-effector pose streaming thread.
    """
    t = 0.0
    while not stop_event.is_set():
        fake_pose = {
            "type": "EE_POSE",
            "position": {
                "x": 0.3,
                "y": 0.1,
                "z": 0.2 + 0.05 * np.sin(t),
            }
        }

        if send_fn is not None:
            send_fn(fake_pose)
        else:
            print(f"[FAKE EE STREAM] {fake_pose}")

        t += 0.1
        time.sleep(1.0 / 30.0)  # 30 Hz


# =========================
# Main grasp function
# =========================

def run_fr3_cart_grasp(
    object_position: np.ndarray,
    object_rotation: np.ndarray,
    object_center: np.ndarray,
    object_width: float,
    send_fn: Callable[[dict], None] | None = None,
):
    """
    Minimal grasp skeleton with fake EE pose streaming.
    """

    print("\n[FR3 GRASP STARTED]")
    print(f"Object position: {object_position}")
    print(f"Object rotation (quat): {object_rotation}")
    print(f"Object center: {object_center}")
    print(f"Object width: {object_width}")

    # -------------------------
    # Sanity checks
    # -------------------------
    assert isinstance(object_position, np.ndarray) and object_position.shape == (3,)
    assert isinstance(object_rotation, np.ndarray) and object_rotation.shape == (4,)
    assert isinstance(object_center, np.ndarray) and object_center.shape == (3,)
    assert isinstance(object_width, float)

    # -------------------------
    # Start fake EE streaming
    # -------------------------
    stop_event = threading.Event()
    stream_thread = threading.Thread(
        target=_fake_ee_pose_stream,
        args=(stop_event, send_fn),
        daemon=True,
    )
    stream_thread.start()

    # -------------------------
    # Placeholder grasp steps
    # -------------------------
    print("[FR3] move_home() (placeholder)")
    time.sleep(1.0)

    print("[FR3] gripper.open() (placeholder)")
    time.sleep(1.0)

    print("[FR3] set_cartesian(target pose) (placeholder)")
    time.sleep(2.0)

    print(f"[FR3] gripper.set_width({object_width}) (placeholder)")
    time.sleep(1.0)

    print("[FR3] move_home() (placeholder)")
    time.sleep(2.0)

    print("[FR3] gripper.open() (placeholder)")
    time.sleep(1.0)

    # -------------------------
    # Stop EE streaming
    # -------------------------
    stop_event.set()
    stream_thread.join()

    # -------------------------
    # Optional completion signal
    # -------------------------
    if send_fn is not None:
        send_fn({
            "type": "GRASP_DONE",
            "success": True
        })

    print("[FR3 GRASP FINISHED]\n")
