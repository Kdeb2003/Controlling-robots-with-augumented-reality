import socket
import json


HOST = "127.0.0.1"
PORT = 5000


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # ---- send GRASP command ----
    grasp_msg = {
        "command": "grasp",
        "item": {
            "object_id": "test-uuid",
            "object_cat": "cube",
            "object_pos": {"x": 0.32, "y": 0.0, "z": 0.14},
            "object_rot": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
            "object_center": {"x": 0.32, "y": 0.0, "z": 0.14},
            "object_wid": 0.05,
            "object_scale": {"x": 1, "y": 1, "z": 1},
            "object_mat": "Blue",
        },
    }

    sock.sendall((json.dumps(grasp_msg) + "\n").encode("utf-8"))
    print("[QUEST] Sent GRASP command\n")

    # ---- receive EE poses ----
    buffer = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break

        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            msg = json.loads(line.decode("utf-8"))
            print("[QUEST] Received:", msg)

            if msg.get("type") == "GRASP_DONE":
                print("\n[QUEST] Grasp finished")
                sock.close()
                return


if __name__ == "__main__":
    main()
