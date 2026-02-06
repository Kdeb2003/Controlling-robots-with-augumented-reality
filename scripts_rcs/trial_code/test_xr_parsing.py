"""
test_xr_parsing.py

Minimal test to verify that:
- object position
- object rotation
- object center
- object width

are correctly available from XR JSON.
"""

import numpy as np
from xr_utils import parse_xr_message


def main():
    # -------------------------
    # Mock XR JSON (from Quest)
    # -------------------------
    xr_msg = {
        "command": "grasp",
        "item": {
            "object_id": "test-uuid",
            "object_cat": "cube",

            "object_pos": {"x": 0.32, "y": 0.00, "z": 0.14},
            "object_rot": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
            "object_center": {"x": 0.32, "y": 0.00, "z": 0.14},

            "object_wid": 0.05,
            "object_scale": {"x": 1.0, "y": 1.0, "z": 1.0},
            "object_mat": "Blue",
        }
    }

    print("\n[TEST] Parsing XR message...\n")
    parsed = parse_xr_message(xr_msg)

    # -------------------------
    # Extract values
    # -------------------------
    item = parsed["item"]

    pos = item["position"]
    rot = item["rotation"]
    center = item["center"]
    width = item["object_width"]

    # -------------------------
    # Print results
    # -------------------------
    print("[RESULTS]")
    print(f"Position (robot frame): {pos}")
    print(f"Rotation (robot frame quat): {rot}")
    print(f"Center (robot frame): {center}")
    print(f"Width: {width}")

    # -------------------------
    # Simple sanity checks
    # -------------------------
    assert isinstance(pos, np.ndarray) and pos.shape == (3,)
    assert isinstance(rot, np.ndarray) and rot.shape == (4,)
    assert isinstance(center, np.ndarray) and center.shape == (3,)
    assert isinstance(width, float)

    print("\n[TEST PASSED] All required fields are available ✅\n")


if __name__ == "__main__":
    main()
