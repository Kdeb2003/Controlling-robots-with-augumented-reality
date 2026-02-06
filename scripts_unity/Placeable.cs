using UnityEngine;
[RequireComponent(typeof(Rigidbody))]
public class Placeable : MonoBehaviour
{
    Rigidbody rb; Renderer rend; Vector3 baseScale; Quaternion baseRot;
    void Awake(){ rb=GetComponent<Rigidbody>(); rend=GetComponentInChildren<Renderer>();
                  baseScale=transform.localScale; baseRot=transform.localRotation; }
    public void BeginPlacement(){ rb.isKinematic=true; rb.useGravity=false; }
    public void CommitPlacement(){ rb.isKinematic=false; rb.useGravity=true; }
    public void SetUniformScale(float s){ transform.localScale=Vector3.one*s; }
    public void SetRotX(float d){ var e=transform.localEulerAngles; e.x=d; transform.localEulerAngles=e; }
    public void SetRotY(float d){ var e=transform.localEulerAngles; e.y=d; transform.localEulerAngles=e; }
    public void SetRotZ(float d){ var e=transform.localEulerAngles; e.z=d; transform.localEulerAngles=e; }
    public void SetMaterial(Material m){ if(rend) rend.material=m; }
    public void ResetAll(){ transform.localScale=baseScale; transform.localRotation=baseRot; }
    public void Delete(){ Destroy(gameObject); if(SelectionManager.I.current==this) SelectionManager.I.Clear(); }
}
