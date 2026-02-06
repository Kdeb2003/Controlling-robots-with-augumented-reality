using UnityEngine;

public class PropertyPanel : MonoBehaviour
{
    public Material[] materials;             // assign 5 materials in Inspector
    Placeable P => SelectionManager.I.current;

    public void OnScale(float v){ if(P) P.SetUniformScale(v); }
    public void OnRotX(float v){ if(P) P.SetRotX(v); }
    public void OnRotY(float v){ if(P) P.SetRotY(v); }
    public void OnRotZ(float v){ if(P) P.SetRotZ(v); }
    public void OnMaterial(int i){ if(P && i>=0 && i<materials.Length) P.SetMaterial(materials[i]); }
    public void OnSave(){ if(P) P.CommitPlacement(); }
    public void OnReset(){ if(P) P.ResetAll(); }
    public void OnDelete(){ if(P) P.Delete(); }
}
