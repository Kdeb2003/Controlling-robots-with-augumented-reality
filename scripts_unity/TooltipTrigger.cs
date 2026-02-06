using UnityEngine;
using UnityEngine.EventSystems;

public class TooltipTrigger : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler
{
    public string tooltipText = "";
    public Vector3 tooltipOffset = new Vector3(0f, 0.05f, 0f);

    private RectTransform rectTransform;

    void Awake()
    {
        rectTransform = GetComponent<RectTransform>();
    }

    public void OnPointerEnter(PointerEventData eventData)
    {
        if (TooltipUI.Instance == null)
            return;
        TooltipUI.Instance.Show(tooltipText, rectTransform, tooltipOffset);
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        if (TooltipUI.Instance == null)
            return;
        TooltipUI.Instance.Hide();
    }
}
