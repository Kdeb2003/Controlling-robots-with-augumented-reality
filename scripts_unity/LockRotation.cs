using UnityEngine;

// Keeps the object's rotation fixed to its initial rotation.
public class LockRotation : MonoBehaviour
{
    private Quaternion initialRotation;

    void Awake()
    {
        initialRotation = transform.rotation;
    }

    void LateUpdate()
    {
        transform.rotation = initialRotation;
    }
}
