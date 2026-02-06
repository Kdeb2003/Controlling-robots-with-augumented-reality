# import threading
# import time

# stop_event = threading.Event()


# def background_thread():
#     """
#     This simulates continuous EE pose streaming.
#     """
#     counter = 0
#     while not stop_event.is_set():
#         print(f"[THREAD] running... counter={counter}")
#         counter += 1
#         time.sleep(0.5)


# def blocking_function():
#     """
#     This simulates robot.move_home() (blocking).
#     """
#     print("[MAIN] blocking function started")
#     time.sleep(5)
#     print("[MAIN] blocking function finished")


# def main():
#     print("[MAIN] starting background thread")
#     t = threading.Thread(target=background_thread)
#     t.start()

#     blocking_function()

#     print("[MAIN] stopping background thread")
#     stop_event.set()
#     t.join()

#     print("[MAIN] program finished cleanly")


# if __name__ == "__main__":
#     main()

# import threading
# import time

# stop_event = threading.Event()


# def counter_thread():
#     """
#     Runs continuously until told to stop.
#     """
#     count = 0
#     while not stop_event.is_set():
#         print(f"[COUNTER THREAD] count = {count}")
#         count += 1
#         time.sleep(0.5)


# def main_task():
#     """
#     Finite task (like robot.move_home()).
#     """
#     print("[MAIN] starting main task")

#     for i in range(6):
#         print(f"[MAIN] working... step {i}")
#         time.sleep(1)

#     print("[MAIN] main task finished")


# def main():
#     print("[MAIN] starting counter thread")
#     t = threading.Thread(target=counter_thread)
#     t.start()

#     main_task()

#     print("[MAIN] stopping counter thread")
#     stop_event.set()
#     t.join()

#     print("[MAIN] all tasks complete")


# if __name__ == "__main__":
#     main()

import threading
import time

stop_event = threading.Event()


def counter_thread():
    count = 0
    while not stop_event.is_set():
        print(f"[THREAD] count = {count}")
        count += 1
        time.sleep(0.5)


def blocking_function():
    """
    Simulates robot.move_home():
    blocking, but no sleep in Python code.
    """
    print("[MAIN] blocking function started")

    # Busy wait to simulate blocking C code
    start = time.time()
    while time.time() - start < 5:
        pass

    print("[MAIN] blocking function finished")


def main():
    t = threading.Thread(target=counter_thread)
    t.start()

    blocking_function()

    stop_event.set()
    t.join()

    print("[MAIN] done")


if __name__ == "__main__":
    main()
