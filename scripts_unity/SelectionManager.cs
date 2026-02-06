using UnityEngine;
public class SelectionManager : MonoBehaviour
{
    public static SelectionManager I; void Awake(){ I=this; }
    public Placeable current;
    public void Select(Placeable p){ current=p; }
    public void Clear(){ if(current) current=null; }
}
