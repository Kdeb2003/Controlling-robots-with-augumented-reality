using UnityEngine;

// Creates 4 invisible wall colliders around a BoxCollider work area.
public class WorkAreaWalls : MonoBehaviour
{
    public BoxCollider workArea;
    public float wallThickness = 0.02f;
    public float wallHeight = 0.1f;
    public bool rebuildOnStart = true;

    private const string WallNorth = "Wall_North";
    private const string WallSouth = "Wall_South";
    private const string WallEast = "Wall_East";
    private const string WallWest = "Wall_West";

    void Awake()
    {
        if (rebuildOnStart)
            RebuildWalls();
    }

    void OnValidate()
    {
        if (!Application.isPlaying)
            RebuildWalls();
    }

    public void RebuildWalls()
    {
        if (workArea == null)
            return;

        EnsureWall(WallNorth);
        EnsureWall(WallSouth);
        EnsureWall(WallEast);
        EnsureWall(WallWest);

        Vector3 center = workArea.center;
        Vector3 size = workArea.size;
        float halfX = size.x * 0.5f;
        float halfZ = size.z * 0.5f;

        // North / South (along X axis)
        ConfigureWall(WallNorth,
            new Vector3(0f, wallHeight * 0.5f, halfZ + wallThickness * 0.5f),
            new Vector3(size.x, wallHeight, wallThickness),
            center);
        ConfigureWall(WallSouth,
            new Vector3(0f, wallHeight * 0.5f, -halfZ - wallThickness * 0.5f),
            new Vector3(size.x, wallHeight, wallThickness),
            center);

        // East / West (along Z axis)
        ConfigureWall(WallEast,
            new Vector3(halfX + wallThickness * 0.5f, wallHeight * 0.5f, 0f),
            new Vector3(wallThickness, wallHeight, size.z),
            center);
        ConfigureWall(WallWest,
            new Vector3(-halfX - wallThickness * 0.5f, wallHeight * 0.5f, 0f),
            new Vector3(wallThickness, wallHeight, size.z),
            center);
    }

    void EnsureWall(string name)
    {
        Transform child = transform.Find(name);
        if (child != null && child.GetComponent<BoxCollider>() != null)
            return;

        GameObject wall = child != null ? child.gameObject : new GameObject(name);
        wall.transform.SetParent(transform, false);
        BoxCollider collider = wall.GetComponent<BoxCollider>();
        if (collider == null)
            wall.AddComponent<BoxCollider>();
    }

    void ConfigureWall(string name, Vector3 localOffset, Vector3 size, Vector3 center)
    {
        Transform child = transform.Find(name);
        if (child == null)
            return;
        child.localPosition = center + localOffset;
        child.localRotation = Quaternion.identity;

        BoxCollider collider = child.GetComponent<BoxCollider>();
        collider.isTrigger = false;
        collider.center = Vector3.zero;
        collider.size = size;
    }
}
