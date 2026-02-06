"""
xr_utils.py

XR <-> System utilities:
- TCP communication (newline-delimited JSON)
- Unity <-> Robot (MuJoCo) frame conversions
- 4x4 robot pose -> Unity pose

Conventions:
- Unity axes:  x right, y up, z forward
- Robot axes:  x forward, y left, z up
- Quaternion order: x, y, z, w
"""

import json
import socket
from typing import Dict, Any, Generator, Sequence, Union

import numpy as np
from scipy.spatial.transform import Rotation as R


# =========================
# Axis mapping
# =========================
# robot = [ z, -x, y ]
# unity = [ -y, z, x ]

AXIS_MAP = np.array(
    [
        [0,  0,  1],   # robot x <- unity z
        [-1, 0,  0],   # robot y <- -unity x
        [0,  1,  0],   # robot z <- unity y
    ],
    dtype=np.float64
)


# =========================
# Position conversions
# =========================

def unity_pos_to_robot(pos: Union[Dict[str, float], Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Unity position -> robot position
    Accepts dict {x,y,z} or array-like [x,y,z].
    """
    if isinstance(pos, dict):
        x, y, z = pos["x"], pos["y"], pos["z"]
    else:
        arr = np.asarray(pos, dtype=np.float64).reshape(3)
        x, y, z = float(arr[0]), float(arr[1]), float(arr[2])
    return np.array([z, -x, y], dtype=np.float64)


def robot_pos_to_unity(pos: np.ndarray) -> Dict[str, float]:
    """
    Robot position -> Unity position
    """
    return {
        "x": -float(pos[1]),
        "y": float(pos[2]),
        "z": float(pos[0]),
    }


# =========================
# Quaternion conversions
# =========================

def unity_quat_to_robot(q_unity: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Unity quaternion -> robot quaternion
    q_unity: [x, y, z, w]
    """
    q = np.asarray(q_unity, dtype=np.float64).reshape(4)
    R_u = R.from_quat(q).as_matrix()
    R_r = AXIS_MAP @ R_u @ AXIS_MAP.T
    return R.from_matrix(R_r).as_quat()


def robot_quat_to_unity(q_robot: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Robot quaternion -> Unity quaternion
    q_robot: [x, y, z, w]
    """
    q = np.asarray(q_robot, dtype=np.float64).reshape(4)
    R_r = R.from_quat(q).as_matrix()
    R_u = AXIS_MAP.T @ R_r @ AXIS_MAP
    return R.from_matrix(R_u).as_quat()


# =========================
# Quaternion -> RPY helpers
# =========================

def unity_quat_to_robot_rpy(q_unity: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    Unity quaternion -> robot RPY (roll, pitch, yaw), radians.
    """
    q_robot = unity_quat_to_robot(q_unity)
    rpy = R.from_quat(q_robot).as_euler("xyz", degrees=False)
    return np.asarray(rpy, dtype=np.float64)


# =========================
# Full pose conversions
# =========================

def robot_pose_4x4_to_unity(T: np.ndarray) -> Dict[str, Any]:
    """
    Convert robot 4x4 homogeneous transform to Unity pose dict.

    T:
        [ R(3x3)  t(3x1) ]
        [ 0 0 0     1   ]
    """
    if T.shape != (4, 4):
        raise ValueError("Expected 4x4 homogeneous transform")

    # Translation
    pos_robot = T[:3, 3]
    pos_unity = robot_pos_to_unity(pos_robot)

    # Rotation
    R_r = T[:3, :3]
    R_u = AXIS_MAP.T @ R_r @ AXIS_MAP
    quat_unity = R.from_matrix(R_u).as_quat()

    return {
        "position": pos_unity,
        "rotation": {
            "x": float(quat_unity[0]),
            "y": float(quat_unity[1]),
            "z": float(quat_unity[2]),
            "w": float(quat_unity[3]),
        }
    }


# =========================
# TCP client (Quest <-> System)
# =========================

class XRTCPClient:
    """
    Newline-delimited JSON TCP client.
    Compatible with your existing protocol.
    """

    def __init__(self, host: str, port: int, timeout: float | None = 2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self.buffer = b""

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.timeout is not None:
            self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def send(self, msg: Dict[str, Any]):
        if self.sock is None:
            raise RuntimeError("TCP socket not connected")
        data = (json.dumps(msg) + "\n").encode("utf-8")
        self.sock.sendall(data)

    def receive(self) -> Generator[Dict[str, Any], None, None]:
        """
        Generator yielding decoded JSON messages.
        """
        if self.sock is None:
            raise RuntimeError("TCP socket not connected")

        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                return
            self.buffer += chunk
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                if not line:
                    continue
                yield json.loads(line.decode("utf-8-sig"))


# =========================
# XR message parsing (NEW)
# =========================

def _vec3_from_dict(d: Dict[str, float]) -> np.ndarray:
    return np.array([d["x"], d["y"], d["z"]], dtype=np.float64)


def _quat_from_dict(d: Dict[str, float]) -> np.ndarray:
    # Unity quaternion order: x, y, z, w
    return np.array([d["x"], d["y"], d["z"], d["w"]], dtype=np.float64)


def parse_xr_item_to_robot(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert XR item JSON into robot-frame data.
    Expected item schema:
    {
      object_id, object_cat,
      object_pos, object_rot, object_center,
      object_wid, object_scale, object_mat
    }
    """

    # Unity-frame data
    unity_pos = _vec3_from_dict(item["object_pos"])
    unity_center = _vec3_from_dict(item["object_center"])
    unity_quat = _quat_from_dict(item["object_rot"])

    # Unity -> Robot frame
    robot_pos = unity_pos_to_robot({
        "x": unity_pos[0],
        "y": unity_pos[1],
        "z": unity_pos[2],
    })

    robot_center = unity_pos_to_robot({
        "x": unity_center[0],
        "y": unity_center[1],
        "z": unity_center[2],
    })

    robot_quat = unity_quat_to_robot(unity_quat)

    return {
        # identity / semantics
        "object_id": item["object_id"],
        "object_cat": item["object_cat"],
        "object_mat": item.get("object_mat", ""),
        "object_scale": item.get("object_scale", None),

        # geometry
        "object_width": item["object_wid"],

        # robot-frame pose
        "position": robot_pos,      # np.ndarray (3,)
        "rotation": robot_quat,     # np.ndarray (4,)
        "center": robot_center,     # np.ndarray (3,)
    }


def parse_xr_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse XR message of the form:
    {
      "command": "grasp" | "push",
      "item": { ... }
    }
    """

    if "command" not in msg:
        raise ValueError("XR message missing 'command'")

    if "item" not in msg:
        raise ValueError("XR message missing 'item'")

    command = msg["command"].lower()
    if command not in ("grasp", "push"):
        raise ValueError(f"Unknown XR command: {command}")

    robot_item = parse_xr_item_to_robot(msg["item"])

    return {
        "command": command,
        "item": robot_item,
    }
