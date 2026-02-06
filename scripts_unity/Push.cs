using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using UnityEngine;

public class Push : MonoBehaviour
{
    [Header("Network")]
    public string robotIp = "172.20.10.7";
    public int robotPort = 5000;

    [Header("Push Settings")]
    [Tooltip("Offset added to EE pose Y (Unity up) to account for gripper half-width.")]
    public float gripperYOffset = 0.0f;
    [Header("References")]
    public ObjectSpawner spawner;

    private readonly TcpClientHandler client = new TcpClientHandler();
    private readonly ConcurrentQueue<string> inbound = new ConcurrentQueue<string>();
    private string activeObjectId;

    [Serializable]
    private class PushCommand
    {
        public string command;
        public PushItem item;
    }

    [Serializable]
    private class PushItem
    {
        public string object_id;
        public string object_cat;
        public ObjectSpawner.Vector3Data object_pos;
        public ObjectSpawner.QuaternionData object_rot;
        public ObjectSpawner.Vector3Data object_center;
        public float object_wid;
        public ObjectSpawner.Vector3Data object_scale;
        public string object_mat;
    }

    [Serializable]
    private class PoseData
    {
        public float x;
        public float y;
        public float z;
    }

    [Serializable]
    private class RobotMessage
    {
        public string type;
        public PoseData position;
    }

    void Awake()
    {
        client.OnMessage += msg => inbound.Enqueue(msg);
    }

    public async void StartPush()
    {
        if (spawner == null)
        {
            Debug.LogWarning("Push: spawner is not assigned.");
            return;
        }

        if (!spawner.TryGetRandomObject(out var data))
        {
            Debug.LogWarning("Push: no spawned objects to select.");
            return;
        }

        activeObjectId = data.id;
        Debug.Log($"Push: selected object id {activeObjectId}");
        PushCommand cmd = new PushCommand
        {
            command = "push",
            item = new PushItem
            {
                object_id = data.id,
                object_cat = data.object_category,
                object_pos = data.object_position,
                object_rot = data.object_rotation,
                object_center = data.center,
                object_wid = data.size.x,
                object_scale = data.size,
                object_mat = data.texture
            }
        };

        string json = JsonUtility.ToJson(cmd);

        try
        {
            await client.ConnectAsync(robotIp, robotPort);
            await client.SendLineAsync(json);
            Debug.Log($"Push sent: {json}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Push TCP error: {ex.Message}");
        }
    }

    void Update()
    {
        while (inbound.TryDequeue(out string msg))
        {
            HandleMessage(msg);
        }
    }

    private void HandleMessage(string msg)
    {
        Debug.Log($"Push: received {msg}");
        RobotMessage parsed;
        try
        {
            parsed = JsonUtility.FromJson<RobotMessage>(msg);
        }
        catch
        {
            return;
        }

        if (parsed == null || string.IsNullOrEmpty(parsed.type))
            return;

        if (parsed.type == "EE_POSE" && parsed.position != null)
        {
            if (spawner != null && spawner.TryGetObjectById(activeObjectId, out GameObject obj))
            {
                Vector3 pos = new Vector3(parsed.position.x, parsed.position.y, parsed.position.z);
                pos.y += gripperYOffset;
                pos = spawner.LocalOriginToWorld(pos);
                if (spawner.clampMovementToWorkArea)
                    pos = spawner.ClampToWorkArea(pos, spawner.lockMovementToSurfaceY);
                obj.transform.position = pos;
            }
        }
        else if (parsed.type == "PUSH_DONE")
        {
            activeObjectId = null;
        }
    }

    void OnDestroy()
    {
        client.Close();
    }
}
