using UnityEngine;

// Applies a simple X-axis shear to the object's mesh for a "skew" effect.
public class SkewableObject : MonoBehaviour
{
    public float maxSkew = 0.5f;

    private MeshFilter meshFilter;
    private MeshCollider meshCollider;
    private Vector3[] baseVertices;
    private Mesh runtimeMesh;

    void Awake()
    {
        meshFilter = GetComponentInChildren<MeshFilter>();
        if (meshFilter == null)
            return;

        if (meshFilter.sharedMesh == null || !meshFilter.sharedMesh.isReadable)
        {
            Debug.LogWarning("SkewableObject: Mesh is not readable. Enable Read/Write in the mesh import settings to allow skew.");
            enabled = false;
            return;
        }

        runtimeMesh = Instantiate(meshFilter.sharedMesh);
        runtimeMesh.name = meshFilter.sharedMesh.name + "_Skewed";
        meshFilter.sharedMesh = runtimeMesh;

        baseVertices = runtimeMesh.vertices;
        meshCollider = GetComponentInChildren<MeshCollider>();
        if (meshCollider != null)
            meshCollider.sharedMesh = runtimeMesh;
    }

    public void SetSkew(float value)
    {
        if (runtimeMesh == null || baseVertices == null)
            return;

        float skew = Mathf.Clamp(value, -maxSkew, maxSkew);
        Vector3[] verts = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++)
        {
            Vector3 v = baseVertices[i];
            v.x += v.y * skew;
            verts[i] = v;
        }

        runtimeMesh.vertices = verts;
        runtimeMesh.RecalculateBounds();
        runtimeMesh.RecalculateNormals();
        if (meshCollider != null)
            meshCollider.sharedMesh = runtimeMesh;
    }
}
