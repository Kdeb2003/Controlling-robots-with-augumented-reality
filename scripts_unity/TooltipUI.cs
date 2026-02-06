using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class TooltipUI : MonoBehaviour
{
    public static TooltipUI Instance;

    public TextMeshProUGUI label;
    public RectTransform background;
    public Vector2 padding = new Vector2(8f, 4f);
    public Vector2 maxSize = new Vector2(200f, 60f);
    private CanvasGroup canvasGroup;

    void Awake()
    {
        Instance = this;
        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        canvasGroup.alpha = 0f;
        canvasGroup.interactable = false;
        canvasGroup.blocksRaycasts = false;
    }

    public void Show(string text, RectTransform target, Vector3 offset)
    {
        if (label == null || target == null)
            return;

        label.text = text;
        Vector2 preferred = label.GetPreferredValues(text);
        preferred.x = Mathf.Min(preferred.x, maxSize.x);
        preferred.y = Mathf.Min(preferred.y, maxSize.y);
        label.rectTransform.sizeDelta = preferred;
        if (background != null)
            background.sizeDelta = preferred + padding * 2f;

        Vector3 worldPos = target.position
            + target.right * offset.x
            + target.up * offset.y
            + target.forward * offset.z;
        transform.position = worldPos;
        transform.rotation = target.rotation;
        transform.SetAsLastSibling();
        canvasGroup.alpha = 1f;
    }

    public void Hide()
    {
        canvasGroup.alpha = 0f;
    }
}
