import numpy as np
from fr3_cart_grasp import run_fr3_cart_grasp


def main():
    run_fr3_cart_grasp(
        object_position=np.array([0.3, 0.1, 0.2]),
        object_rotation=np.array([0.0, 0.0, 0.0, 1.0]),
        object_center=np.array([0.3, 0.1, 0.2]),
        object_width=0.05,
    )


if __name__ == "__main__":
    main()
