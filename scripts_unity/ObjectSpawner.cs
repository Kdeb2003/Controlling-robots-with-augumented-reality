using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

public class ObjectSpawner : MonoBehaviour
{
    public Button sphereButton;
    public Button cubeButton;
    public Button cylinderButton;
    public Button localOriginButton;
    public Button[] toolbarButtons;
    public Button grabButton;
    public Button pushButton;

    public Button textureToggleButton;
    public GameObject texturePanel;
    public Button[] textureButtons;

    public ObjectSettingsManager settingsManager;
    public Button settingsToggleButton;
    public Grasp graspHandler;
    public Push pushHandler;

    public Transform spawnPoint;
    [Header("Work Area")]
    public BoxCollider workArea;
    public bool clampSpawnToWorkArea = true;
    public bool clampMovementToWorkArea = true;
    public bool lockMovementToSurfaceY = false;
    public float spawnHeightOffset = 0.02f;

    public GameObject grabbableCubePrefab;
    public GameObject grabbableSpherePrefab;
    public GameObject grabbableCylinderPrefab;
    public GameObject grabbablePyramidPrefab;
    public GameObject grabbableStarPrefab;
    public GameObject grabbableDonutPrefab;
    public GameObject grabbableClothPrefab;
    public GameObject grabbableBowlPrefab;
    public GameObject grabbableCupPrefab;
    public GameObject grabbableStonePrefab;

    public Material[] textureMaterials;
    public Vector3 spawnScale = Vector3.one;
    public float spawnSkew = 0f;

    public GameObject localOriginPrefab;
    public Vector3 sphereScale = Vector3.one;
    public string dataFileName = "spawned_objects.json";
    public float liveUpdateIntervalSeconds = 0.2f;

    private int spawnIndex;
    private Transform localOrigin;
    private readonly List<SpawnedObjectData> spawnedObjects = new List<SpawnedObjectData>();
    private readonly Dictionary<string, GameObject> spawnedObjectLookup = new Dictionary<string, GameObject>();
    private int selectedTextureIndex = -1;

    void Start()
    {
        if (sphereButton != null)
            sphereButton.onClick.AddListener(SpawnSphere);
        if (cubeButton != null)
            cubeButton.onClick.AddListener(SpawnCube);
        if (cylinderButton != null)
            cylinderButton.onClick.AddListener(SpawnCylinder);
        if (localOriginButton != null)
            localOriginButton.onClick.AddListener(SpawnLocalOrigin);

        if (textureToggleButton != null)
            textureToggleButton.onClick.AddListener(ToggleTexturePanel);
        if (settingsToggleButton != null && settingsManager != null)
            settingsToggleButton.onClick.AddListener(settingsManager.Show);

        HookToolbarButtons();
        HookTextureButtons();
        HookActionButtons();

        if (texturePanel != null)
            texturePanel.SetActive(false);
    }

    void Update()
    {
#if UNITY_EDITOR
        var keyboard = Keyboard.current;
        if (keyboard == null)
            return;
        bool ctrlDown = keyboard.leftCtrlKey.isPressed || keyboard.rightCtrlKey.isPressed;
        if (ctrlDown && keyboard.cKey.wasPressedThisFrame)
            SpawnToolbarIndex(7);
        if (ctrlDown && keyboard.sKey.wasPressedThisFrame)
            SpawnToolbarIndex(8);
        if (ctrlDown && keyboard.vKey.wasPressedThisFrame)
            SpawnToolbarIndex(9);
#endif
    }

    public void SpawnSphere()
    {
        Debug.Log("SpawnSphere clicked");
        if (grabbableSpherePrefab == null)
        {
            Debug.LogWarning("Grabbable sphere prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject sphere = Instantiate(grabbableSpherePrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(sphere);
        ApplySpawnSkew(sphere);
        ApplySelectedMaterial(sphere);
        sphere.name = "SpawnedSphere_" + (++spawnIndex);
        var rb = sphere.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = sphere.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(sphere, "sphere");
        AttachTracker(sphere, id, "sphere");
    }

    public void SpawnCube()
    {
        Debug.Log("SpawnCube clicked");
        if (grabbableCubePrefab == null)
        {
            Debug.LogWarning("Grabbable cube prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject cube = Instantiate(grabbableCubePrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(cube);
        ApplySpawnSkew(cube);
        ApplySelectedMaterial(cube);
        cube.name = "SpawnedCube_" + (++spawnIndex);
        var rb = cube.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = cube.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(cube, "cube");
        AttachTracker(cube, id, "cube");
    }

    public void SpawnCylinder()
    {
        Debug.Log("SpawnCylinder clicked");
        if (grabbableCylinderPrefab == null)
        {
            Debug.LogWarning("Grabbable cylinder prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject cylinder = Instantiate(grabbableCylinderPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(cylinder);
        ApplySpawnSkew(cylinder);
        ApplySelectedMaterial(cylinder);
        cylinder.name = "SpawnedCylinder_" + (++spawnIndex);
        var rb = cylinder.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = cylinder.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(cylinder, "cylinder");
        AttachTracker(cylinder, id, "cylinder");
    }

    public void SpawnPyramid()
    {
        Debug.Log("SpawnPyramid clicked");
        if (grabbablePyramidPrefab == null)
        {
            Debug.LogWarning("Grabbable pyramid prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject pyramid = Instantiate(grabbablePyramidPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(pyramid);
        ApplySpawnSkew(pyramid);
        ApplySelectedMaterial(pyramid);
        pyramid.name = "SpawnedPyramid_" + (++spawnIndex);
        var rb = pyramid.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = pyramid.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(pyramid, "pyramid");
        AttachTracker(pyramid, id, "pyramid");
    }

    public void SpawnStar()
    {
        Debug.Log("SpawnStar clicked");
        if (grabbableStarPrefab == null)
        {
            Debug.LogWarning("Grabbable star prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject star = Instantiate(grabbableStarPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(star);
        ApplySpawnSkew(star);
        ApplySelectedMaterial(star);
        star.name = "SpawnedStar_" + (++spawnIndex);
        var rb = star.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = star.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(star, "star");
        AttachTracker(star, id, "star");
    }

    public void SpawnDonut()
    {
        Debug.Log("SpawnDonut clicked");
        if (grabbableDonutPrefab == null)
        {
            Debug.LogWarning("Grabbable donut prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject donut = Instantiate(grabbableDonutPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(donut);
        ApplySpawnSkew(donut);
        ApplySelectedMaterial(donut);
        donut.name = "SpawnedDonut_" + (++spawnIndex);
        var rb = donut.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = donut.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(donut, "donut");
        AttachTracker(donut, id, "donut");
    }

    public void SpawnCloth()
    {
        Debug.Log("SpawnCloth clicked");
        if (grabbableClothPrefab == null)
        {
            Debug.LogWarning("Grabbable cloth prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject cloth = Instantiate(grabbableClothPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(cloth);
        ApplySpawnSkew(cloth);
        ApplySelectedMaterial(cloth);
        cloth.name = "SpawnedCloth_" + (++spawnIndex);
        var rb = cloth.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = cloth.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(cloth, "cloth");
        AttachTracker(cloth, id, "cloth");
    }

    public void SpawnBowl()
    {
        Debug.Log("SpawnBowl clicked");
        if (grabbableBowlPrefab == null)
        {
            Debug.LogWarning("Grabbable bowl prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject bowl = Instantiate(grabbableBowlPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(bowl);
        ApplySpawnSkew(bowl);
        ApplySelectedMaterial(bowl);
        bowl.name = "SpawnedBowl_" + (++spawnIndex);
        var rb = bowl.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = bowl.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(bowl, "bowl");
        AttachTracker(bowl, id, "bowl");
    }

    public void SpawnCup()
    {
        Debug.Log("SpawnCup clicked");
        if (grabbableCupPrefab == null)
        {
            Debug.LogWarning("Grabbable cup prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject cup = Instantiate(grabbableCupPrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(cup);
        ApplySpawnSkew(cup);
        ApplySelectedMaterial(cup);
        cup.name = "SpawnedCup_" + (++spawnIndex);
        var rb = cup.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = cup.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(cup, "cup");
        AttachTracker(cup, id, "cup");
    }

    public void SpawnStone()
    {
        Debug.Log("SpawnStone clicked");
        if (grabbableStonePrefab == null)
        {
            Debug.LogWarning("Grabbable stone prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject stone = Instantiate(grabbableStonePrefab, spawnPosition, spawnPoint.rotation);
        ApplySpawnScale(stone);
        ApplySpawnSkew(stone);
        ApplySelectedMaterial(stone);
        stone.name = "SpawnedStone_" + (++spawnIndex);
        var rb = stone.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = true;
            rb.isKinematic = false;
        }
        var col = stone.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;
        string id = RecordObject(stone, "stone");
        AttachTracker(stone, id, "stone");
    }

    void SpawnLocalOrigin()
    {
        if (localOrigin != null)
            Destroy(localOrigin.gameObject);
        if (localOriginPrefab == null)
        {
            Debug.LogWarning("Local origin prefab is not assigned.");
            return;
        }

        Vector3 spawnPosition = GetSpawnPosition();
        GameObject origin = Instantiate(localOriginPrefab, spawnPosition, Quaternion.identity);
        origin.name = "LocalOrigin";
        localOrigin = origin.transform;
        localOrigin.rotation = Quaternion.identity;

        var rb = origin.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.useGravity = false;
            rb.isKinematic = true;
            rb.constraints = RigidbodyConstraints.FreezeRotation;
        }
        var col = origin.GetComponent<Collider>();
        if (col != null)
            col.isTrigger = false;

        // Keep spawnPoint independent; localOrigin is only for coordinate conversion.
    }


    void ApplySpawnScale(GameObject obj)
    {
        if (obj == null)
            return;
        obj.transform.localScale = Vector3.Scale(obj.transform.localScale, spawnScale);
    }

    void ApplySpawnSkew(GameObject obj)
    {
        if (obj == null)
            return;
        if (Mathf.Abs(spawnSkew) < 0.0001f)
            return;
        SkewableObject skewable = obj.GetComponent<SkewableObject>();
        if (skewable == null)
            skewable = obj.AddComponent<SkewableObject>();
        skewable.SetSkew(spawnSkew);
    }


    void HookToolbarButtons()
    {
        if (toolbarButtons == null)
            return;
        for (int i = 0; i < toolbarButtons.Length; i++)
        {
            Button button = toolbarButtons[i];
            if (button == null)
                continue;
            int index = i;
            button.onClick.AddListener(() => SpawnToolbarIndex(index));
        }
    }

    void HookActionButtons()
    {
        if (grabButton != null)
            grabButton.onClick.AddListener(OnGrabClicked);
        if (pushButton != null)
            pushButton.onClick.AddListener(OnPushClicked);
    }

    void OnGrabClicked()
    {
        Debug.Log("Grab button clicked");
        if (graspHandler != null)
            graspHandler.StartGrasp();
    }

    void OnPushClicked()
    {
        Debug.Log("Push button clicked");
        if (pushHandler != null)
            pushHandler.StartPush();
    }

    void SpawnToolbarIndex(int index)
    {
        switch (index)
        {
            case 0:
                SpawnCube();
                break;
            case 1:
                SpawnSphere();
                break;
            case 2:
                SpawnCylinder();
                break;
            case 3:
                SpawnPyramid();
                break;
            case 4:
                SpawnStar();
                break;
            case 5:
                SpawnDonut();
                break;
            case 6:
                SpawnCloth();
                break;
            case 7:
                SpawnBowl();
                break;
            case 8:
                SpawnCup();
                break;
            case 9:
                SpawnStone();
                break;
        }
    }

    void HookTextureButtons()
    {
        if (textureButtons == null)
            return;
        for (int i = 0; i < textureButtons.Length; i++)
        {
            Button button = textureButtons[i];
            if (button == null)
                continue;
            int index = i;
            button.onClick.AddListener(() => SelectTexture(index));
        }
    }

    void ToggleTexturePanel()
    {
        if (texturePanel == null)
            return;
        texturePanel.SetActive(!texturePanel.activeSelf);
    }

    void SelectTexture(int index)
    {
        if (textureMaterials == null || index < 0 || index >= textureMaterials.Length)
            return;
        selectedTextureIndex = index;
        if (texturePanel != null)
            texturePanel.SetActive(false);
    }

    void ApplySelectedMaterial(GameObject obj)
    {
        if (obj == null || textureMaterials == null)
            return;
        if (selectedTextureIndex < 0 || selectedTextureIndex >= textureMaterials.Length)
            return;
        Renderer renderer = obj.GetComponentInChildren<Renderer>();
        if (renderer == null)
            return;
        renderer.material = textureMaterials[selectedTextureIndex];
    }

    Vector3 GetSpawnPosition()
    {
        if (workArea != null && clampSpawnToWorkArea)
        {
            Vector3 local = GetRandomPointOnWorkArea();
            return workArea.transform.TransformPoint(local);
        }
        if (spawnPoint == null)
            return Vector3.zero;
        return spawnPoint.position;
    }

    Vector3 GetRandomPointOnWorkArea()
    {
        Vector3 center = workArea.center;
        Vector3 half = workArea.size * 0.5f;
        float x = UnityEngine.Random.Range(-half.x, half.x);
        float z = UnityEngine.Random.Range(-half.z, half.z);
        Vector3 local = center + new Vector3(x, 0f, z);
        local.y = center.y + half.y + spawnHeightOffset;
        return local;
    }

    public Vector3 ClampToWorkArea(Vector3 worldPosition, bool lockToSurface)
    {
        if (workArea == null)
            return worldPosition;

        Transform areaTransform = workArea.transform;
        Vector3 local = areaTransform.InverseTransformPoint(worldPosition);
        Vector3 center = workArea.center;
        Vector3 half = workArea.size * 0.5f;

        local -= center;
        local.x = Mathf.Clamp(local.x, -half.x, half.x);
        local.z = Mathf.Clamp(local.z, -half.z, half.z);
        if (lockToSurface)
            local.y = half.y + spawnHeightOffset;
        local += center;

        return areaTransform.TransformPoint(local);
    }

    string RecordObject(GameObject obj, string category)
    {
        if (obj == null)
            return "";

        Renderer renderer = obj.GetComponentInChildren<Renderer>();
        Vector3 worldPosition = obj.transform.position;
        Quaternion worldRotation = obj.transform.rotation;
        Vector3 worldCenter = renderer != null ? renderer.bounds.center : worldPosition;
        Vector3 size = renderer != null ? renderer.bounds.size : Vector3.one;
        string textureName = renderer != null && renderer.sharedMaterial != null
            ? renderer.sharedMaterial.name
            : "";

        Vector3 position = localOrigin != null
            ? localOrigin.InverseTransformPoint(worldPosition)
            : worldPosition;
        Quaternion rotation = localOrigin != null
            ? Quaternion.Inverse(localOrigin.rotation) * worldRotation
            : worldRotation;
        Vector3 center = localOrigin != null
            ? localOrigin.InverseTransformPoint(worldCenter)
            : worldCenter;

        string id = Guid.NewGuid().ToString();
        SpawnedObjectData data = new SpawnedObjectData
        {
            id = id,
            object_category = category,
            object_position = Vector3Data.FromVector3(position),
            object_rotation = QuaternionData.FromQuaternion(rotation),
            center = Vector3Data.FromVector3(center),
            size = Vector3Data.FromVector3(size),
            texture = textureName
        };
        spawnedObjects.Add(data);
        spawnedObjectLookup[id] = obj;
        WriteJson();
        return id;
    }

    void UpdateRecord(string id, GameObject obj)
    {
        if (string.IsNullOrEmpty(id) || obj == null)
            return;

        int index = -1;
        for (int i = 0; i < spawnedObjects.Count; i++)
        {
            if (spawnedObjects[i].id == id)
            {
                index = i;
                break;
            }
        }
        if (index < 0)
            return;

        Renderer renderer = obj.GetComponentInChildren<Renderer>();
        Vector3 worldPosition = obj.transform.position;
        Quaternion worldRotation = obj.transform.rotation;
        Vector3 worldCenter = renderer != null ? renderer.bounds.center : worldPosition;
        Vector3 size = renderer != null ? renderer.bounds.size : Vector3.one;
        string textureName = renderer != null && renderer.sharedMaterial != null
            ? renderer.sharedMaterial.name
            : "";

        Vector3 position = localOrigin != null
            ? localOrigin.InverseTransformPoint(worldPosition)
            : worldPosition;
        Quaternion rotation = localOrigin != null
            ? Quaternion.Inverse(localOrigin.rotation) * worldRotation
            : worldRotation;
        Vector3 center = localOrigin != null
            ? localOrigin.InverseTransformPoint(worldCenter)
            : worldCenter;

        SpawnedObjectData data = spawnedObjects[index];
        data.object_position = Vector3Data.FromVector3(position);
        data.object_rotation = QuaternionData.FromQuaternion(rotation);
        data.center = Vector3Data.FromVector3(center);
        data.size = Vector3Data.FromVector3(size);
        data.texture = textureName;
        spawnedObjects[index] = data;
        WriteJson();
    }

    void AttachTracker(GameObject obj, string id, string category)
    {
        if (obj == null || string.IsNullOrEmpty(id))
            return;
        SpawnedObjectTracker tracker = obj.AddComponent<SpawnedObjectTracker>();
        tracker.Initialize(this, id, liveUpdateIntervalSeconds);
    }

    void WriteJson()
    {
        SpawnedObjectList wrapper = new SpawnedObjectList { items = spawnedObjects };
        string json = JsonUtility.ToJson(wrapper, true);
        string path = Path.Combine(Application.persistentDataPath, dataFileName);
        File.WriteAllText(path, json);
    }

    [Serializable]
    class SpawnedObjectList
    {
        public List<SpawnedObjectData> items;
    }

    [Serializable]
    public class SpawnedObjectData
    {
        public string id;
        public string object_category;
        public Vector3Data object_position;
        public QuaternionData object_rotation;
        public Vector3Data center;
        public Vector3Data size;
        public string texture;
    }

    [Serializable]
    public struct Vector3Data
    {
        public float x;
        public float y;
        public float z;

        public static Vector3Data FromVector3(Vector3 value)
        {
            return new Vector3Data { x = value.x, y = value.y, z = value.z };
        }
    }

    [Serializable]
    public struct QuaternionData
    {
        public float x;
        public float y;
        public float z;
        public float w;

        public static QuaternionData FromQuaternion(Quaternion value)
        {
            return new QuaternionData { x = value.x, y = value.y, z = value.z, w = value.w };
        }
    }

    public bool TryGetRandomObject(out SpawnedObjectData data)
    {
        data = default;
        if (spawnedObjects.Count == 0)
            return false;
        int index = UnityEngine.Random.Range(0, spawnedObjects.Count);
        data = spawnedObjects[index];
        return true;
    }

    public IReadOnlyList<SpawnedObjectData> GetAllObjects()
    {
        return spawnedObjects;
    }

    public bool TryGetObjectById(string id, out GameObject obj)
    {
        if (string.IsNullOrEmpty(id))
        {
            obj = null;
            return false;
        }
        return spawnedObjectLookup.TryGetValue(id, out obj);
    }

    public Vector3 LocalOriginToWorld(Vector3 localPosition)
    {
        if (localOrigin == null)
            return localPosition;
        return localOrigin.TransformPoint(localPosition);
    }

    class SpawnedObjectTracker : MonoBehaviour
    {
        private ObjectSpawner spawner;
        private string id;
        private float nextWriteTime;
        private float interval;

        public void Initialize(ObjectSpawner owner, string recordId, float updateInterval)
        {
            spawner = owner;
            id = recordId;
            interval = Mathf.Max(0.05f, updateInterval);
            nextWriteTime = Time.unscaledTime + interval;
        }

        void Update()
        {
            if (spawner == null || string.IsNullOrEmpty(id))
                return;
            if (Time.unscaledTime < nextWriteTime)
                return;
            if (!transform.hasChanged)
                return;
            transform.hasChanged = false;
            nextWriteTime = Time.unscaledTime + interval;
            spawner.UpdateRecord(id, gameObject);
        }
    }
}
