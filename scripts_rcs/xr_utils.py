"""
xr_utils.py

XR <-> System utilities:
- TCP communication (newline-delimited JSON)
- Unity <-> Robot (MuJoCo) frame conversions
- 4x4 robot pose -> Unity pose

Conventions:
- Unity axes:  x right, y up, z forward
- Robot axes:  x left, y backward, z up
- Quaternion order: x, y, z, w
"""

import json
import socket
from typing import Dict, Any, Generator

import numpy as np
from scipy.spatial.transform import Rotation as R


# =========================
# Axis mapping
# =========================
# Robot <- Unity
# x_r = -x_u
# y_r = -z_u
# z_r =  y_u

AXIS_MAP = np.array(
    [
        [-1,  0,  0],  # x_r <- -x_u
        [ 0,  0, -1],  # y_r <- -z_u
        [ 0,  1,  0],  # z_r <-  y_u
    ],
    dtype=np.float64
)


# =========================
# Position conversions
# =========================

def unity_pos_to_robot(pos: Dict[str, float]) -> np.ndarray:
    """
    Unity position -> robot position
    """
    return np.array(
        [
            -pos["x"],   # x_r
            -pos["z"],   # y_r
             pos["y"],   # z_r
        ],
        dtype=np.float64
    )


def robot_pos_to_unity(pos: np.ndarray) -> Dict[str, float]:
    """
    Robot position -> Unity position
    """
    return {
        "x": -float(pos[0]),  # x_u
        "y":  float(pos[2]),  # y_u
        "z": -float(pos[1]),  # z_u
    }


# =========================
# Quaternion conversions
# =========================

def unity_quat_to_robot(q_unity: np.ndarray) -> np.ndarray:
    """
    Unity quaternion -> robot quaternion
    q_unity: [x, y, z, w]
    """
    R_u = R.from_quat(q_unity).as_matrix()
    R_r = AXIS_MAP @ R_u @ AXIS_MAP.T
    return R.from_matrix(R_r).as_quat()


def robot_quat_to_unity(q_robot: np.ndarray) -> np.ndarray:
    """
    Robot quaternion -> Unity quaternion
    q_robot: [x, y, z, w]
    """
    R_r = R.from_quat(q_robot).as_matrix()
    R_u = AXIS_MAP.T @ R_r @ AXIS_MAP
    return R.from_matrix(R_u).as_quat()


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
# XR message parsing
# =========================

def _vec3_from_dict(d: Dict[str, float]) -> np.ndarray:
    return np.array([d["x"], d["y"], d["z"]], dtype=np.float64)


def _quat_from_dict(d: Dict[str, float]) -> np.ndarray:
    # Unity quaternion order: x, y, z, w
    return np.array([d["x"], d["y"], d["z"], d["w"]], dtype=np.float64)


def parse_xr_item_to_robot(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert XR item JSON into robot-frame data.
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
        "object_id": item["object_id"],
        "object_cat": item["object_cat"],
        "object_mat": item.get("object_mat", ""),
        "object_scale": item.get("object_scale", None),
        "object_width": item["object_wid"],
        "position": robot_pos,
        "rotation": robot_quat,
        "center": robot_center,
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