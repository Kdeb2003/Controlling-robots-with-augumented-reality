# Controlling Robots with Augmented Reality (AR ↔ FR3)

This repository contains **system-side (Python / RCS)** and **client-side (Unity / Quest)** code
to control a Franka FR3 robot using Augmented Reality.

The pipeline is:

**Unity (Quest) → TCP → XR System Server → Robot Control Stack (RCS) → FR3**
and back via **EE pose streaming**.

---

## Repository Structure

```
controlling-robots-with-AR/
│
├── scripts_rcs/          # Python system-side code (XR server + robot logic)
│   ├── fr3_cart_grasp_xr.py
│   ├── fr3_cart_push_xr.py
│   ├── xr_system_server.py
│   ├── xr_utils.py
│   ├── robot_state_logger.py
│   └── ...
│
├── scripts_unity/        # Unity client-side scripts (Quest / UI)
│   ├── Grasp.cs
│   ├── Push.cs
│   ├── ObjectSpawner.cs
│   ├── TcpClientHandler.cs
│   ├── LockRotation.cs
│   └── ...
│
└── README.md
```

---

## 1. Install Robot Control Stack (RCS)

Clone and install RCS **first**:

```
git clone https://github.com/RobotControlStack/robot-control-stack.git
cd robot-control-stack
```

Create and activate the Python environment (recommended):

```
conda create -n rcs python=3.11
conda activate rcs
```

Install RCS in editable mode:

```
pip install -e .
```

Verify installation:

```
python -c "import rcs; print(rcs.__version__)"
```

---

## 2. Install This Repository (scripts_rcs)

Clone this repository:

```
git clone https://gitos.rrze.fau.de/lit25-26/controlling-robots-with-AR.git
```

Copy **scripts_rcs** into the RCS repository:

```
cp -r controlling-robots-with-AR/scripts_rcs robot-control-stack/
```

Final structure:

```
robot-control-stack/
├── rcs/
├── scripts_rcs/
│   ├── xr_system_server.py
│   ├── fr3_cart_grasp_xr.py
│   ├── fr3_cart_push_xr.py
│   └── xr_utils.py
```

---

## 3. Run the XR System Server (Python)

Activate the RCS environment:

```
conda activate rcs
cd robot-control-stack
```

Run the XR server:

```
python scripts_rcs/xr_system_server.py
```

Expected output:

```
[XR SERVER] Listening on 0.0.0.0:5000
```

This server:
- Receives object JSON from Unity
- Converts Unity → robot frame
- Dispatches `grasp` / `push` logic
- Streams EE pose back to Unity

---

## 4. Unity Client Setup (scripts_unity)

### Folder Structure

Create a folder in your Unity project:

```
Assets/
└── scripts_unity/
    ├── Grasp.cs
    ├── Push.cs
    ├── ObjectSpawner.cs
    ├── TcpClientHandler.cs
    ├── LockRotation.cs
    └── ...
```

Copy all files from `scripts_unity/` into this folder.

---

## 5. Unity Scene Requirements

Required GameObjects:

- **LocalOrigin**
  - Represents robot base frame
  - Must be manually placed on robot base
  - Rotation must be identity

- **WorkArea**
  - BoxCollider defining spawn region

- **TCP Client**
  - Uses `TcpClientHandler.cs`
  - Connects to XR server IP + port

Unity axis convention:

```
X → Right (red)
Y → Up    (green)
Z → Forward (blue)
```

Robot local origin convention:

```
X → robot forward
Y → robot left
Z → robot up
```

---

## 6. Runtime Flow

1. Start XR system server (Python)
2. Start Unity scene on Meta Quest
3. Place **LocalOrigin** at robot base
4. Spawn objects inside work area
5. Press **Grasp** or **Push**
6. Robot executes motion
7. EE pose streams back to Unity

---

## 7. Notes & Tips

- Object positions sent from Unity are **relative to LocalOrigin**
- No world-frame values are used
- Object width is derived from renderer bounds
- Very small values (e-21) are numerical noise → safe to ignore
- EE streaming always sends **center-aligned pose**

---

## 8. Troubleshooting

**Robot jumps downward**
→ Check axis mapping in `xr_utils.py`

**Wrong orientation**
→ Ensure `LocalOrigin.rotation == Quaternion.identity`

**No TCP connection**
→ Verify IP, port, firewall

---

## Authors

LiT 25–26 – Controlling Robots with Augmented Reality  
FAU Erlangen-Nürnberg

---

## License

Academic / Research Use
