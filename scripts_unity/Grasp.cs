using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using UnityEngine;

public class Grasp : MonoBehaviour
{
    [Header("Network")]
    public string robotIp = "172.29.218.144";
    public int robotPort = 5000;

    [Header("References")]
    public ObjectSpawner spawner;

    private readonly TcpClientHandler client = new TcpClientHandler();
    private readonly ConcurrentQueue<string> inbound = new ConcurrentQueue<string>();
    private string activeObjectId;
    private bool hasPhysicsOverride;
    private bool prevUseGravity;
    private bool prevIsKinematic;

    [Serializable]
    private class GraspCommand
    {
        public string command;
        public GraspItem item;
    }

    [Serializable]
    private class GraspItem
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

    public async void StartGrasp()
    {
        if (spawner == null)
        {
            Debug.LogWarning("Grasp: spawner is not assigned.");
            return;
        }

        if (!spawner.TryGetRandomObject(out var data))
        {
            Debug.LogWarning("Grasp: no spawned objects to select.");
            return;
        }

        activeObjectId = data.id;
        ApplyPhysicsOverride(true);
        Debug.Log($"Grasp: selected object id {activeObjectId}");
        GraspCommand cmd = new GraspCommand
        {
            command = "grasp",
            item = new GraspItem
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
            Debug.Log($"Grasp sent: {json}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Grasp TCP error: {ex.Message}");
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
        Debug.Log($"Grasp: received {msg}");
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
                Vector3 target = new Vector3(parsed.position.x, parsed.position.y, parsed.position.z);
                target = spawner.LocalOriginToWorld(target);
                if (spawner.clampMovementToWorkArea)
                    target = spawner.ClampToWorkArea(target, spawner.lockMovementToSurfaceY);
                obj.transform.position = target;
            }
        }
        else if (parsed.type == "GRASP_DONE")
        {
            ApplyPhysicsOverride(false);
            activeObjectId = null;
        }
    }

    void OnDestroy()
    {
        ApplyPhysicsOverride(false);
        client.Close();
    }

    private void ApplyPhysicsOverride(bool enable)
    {
        if (spawner == null || string.IsNullOrEmpty(activeObjectId))
            return;
        if (!spawner.TryGetObjectById(activeObjectId, out GameObject obj))
            return;
        Rigidbody rb = obj.GetComponent<Rigidbody>();
        if (rb == null)
            return;

        if (enable)
        {
            if (!hasPhysicsOverride)
            {
                prevUseGravity = rb.useGravity;
                prevIsKinematic = rb.isKinematic;
                hasPhysicsOverride = true;
            }
            rb.useGravity = false;
            rb.isKinematic = true;
        }
        else if (hasPhysicsOverride)
        {
            rb.useGravity = prevUseGravity;
            rb.isKinematic = prevIsKinematic;
            hasPhysicsOverride = false;
        }
    }
}
