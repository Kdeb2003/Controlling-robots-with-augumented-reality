import socket
import json
import threading

from xr_utils import parse_xr_message
from fr3_cart_grasp import run_fr3_cart_grasp


HOST = "0.0.0.0"
PORT = 5000


def send_line(conn, msg: dict):
    data = (json.dumps(msg) + "\n").encode("utf-8")
    conn.sendall(data)


def handle_client(conn, addr):
    print(f"[SYSTEM] Client connected: {addr}")
    buffer = b""

    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break

            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if not line:
                    continue

                msg = json.loads(line.decode("utf-8"))
                print(f"[SYSTEM] Received:\n{msg}\n")

                parsed = parse_xr_message(msg)

                if parsed["command"] == "grasp":
                    item = parsed["item"]

                    # call grasp logic
                    run_fr3_cart_grasp(
                        object_position=item["position"],
                        object_rotation=item["rotation"],
                        object_center=item["center"],
                        object_width=item["object_width"],
                        send_fn=lambda m: send_line(conn, m),
                    )

    except Exception as e:
        print(f"[SYSTEM] Error: {e}")

    finally:
        conn.close()
        print(f"[SYSTEM] Client disconnected: {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[SYSTEM] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()


if __name__ == "__main__":
    main()
