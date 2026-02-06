import socket
import json
import threading

from xr_utils import parse_xr_message
from fr3_cart_grasp_xr import run_fr3_cart_grasp_xr

try:
    from fr3_cart_push_xr import run_fr3_cart_push_xr
except Exception:
    run_fr3_cart_push_xr = None


HOST = "0.0.0.0"
PORT = 5007


def send_line(conn, msg: dict):
    data = (json.dumps(msg) + "\n").encode("utf-8")
    conn.sendall(data)


def handle_client(conn, addr):
    print(f"[XR SERVER] Client connected: {addr}")
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
                print(f"[XR SERVER] Received message: {msg}") # Debug print
                parsed = parse_xr_message(msg)

                cmd = parsed["command"]
                item = parsed["item"]

                if cmd == "grasp":
                    run_fr3_cart_grasp_xr(
                        object_position=item["position"],
                        object_rotation=item["rotation"],
                        object_center=item["center"],
                        object_width=float(item["object_width"]),
                        object_cat=item["object_cat"],
                        send_fn=lambda m: send_line(conn, m),
                    )

                elif cmd == "push":
                    if run_fr3_cart_push_xr is None:
                        send_line(conn, {"type": "ERROR", "message": "push handler not available"})
                    else:
                        run_fr3_cart_push_xr(
                            object_position=item["position"],
                            object_rotation=item["rotation"],
                            object_center=item["center"],
                            object_width=float(item["object_width"]),
                            send_fn=lambda m: send_line(conn, m),
                        )

                else:
                    send_line(conn, {"type": "ERROR", "message": f"unknown command: {cmd}"})

    except Exception as e:
        print(f"[XR SERVER] Error: {e}")

    finally:
        conn.close()
        print(f"[XR SERVER] Client disconnected: {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[XR SERVER] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()


if __name__ == "__main__":
    main()
