using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ObjectSettingsManager : MonoBehaviour
{
    public GameObject panel;
    public Slider scaleSlider;
    public Slider skewSlider;
    public Button closeButton;
    public TextMeshProUGUI scaleValueText;
    public TextMeshProUGUI skewValueText;
    public ObjectSpawner spawner;

    void Awake()
    {
        if (closeButton != null)
            closeButton.onClick.AddListener(Hide);
        Hide();
    }

    public void Show()
    {
        if (panel == null)
            return;

        if (scaleSlider != null)
        {
            float current = spawner != null ? spawner.spawnScale.x : 1f;
            scaleSlider.SetValueWithoutNotify(current);
            scaleSlider.onValueChanged.RemoveListener(OnScaleChanged);
            scaleSlider.onValueChanged.AddListener(OnScaleChanged);
            UpdateScaleValue(current);
        }

        if (skewSlider != null)
        {
            float currentSkew = spawner != null ? spawner.spawnSkew : 0f;
            skewSlider.SetValueWithoutNotify(currentSkew);
            skewSlider.onValueChanged.RemoveListener(OnSkewChanged);
            skewSlider.onValueChanged.AddListener(OnSkewChanged);
            UpdateSkewValue(currentSkew);
        }

        panel.SetActive(true);
    }

    public void Hide()
    {
        if (panel != null)
            panel.SetActive(false);
    }

    void OnScaleChanged(float value)
    {
        if (spawner == null)
            return;
        spawner.spawnScale = Vector3.one * value;
        UpdateScaleValue(value);
    }

    void OnSkewChanged(float value)
    {
        if (spawner == null)
            return;
        spawner.spawnSkew = value;
        UpdateSkewValue(value);
    }

    void UpdateScaleValue(float value)
    {
        if (scaleValueText != null)
            scaleValueText.text = value.ToString("0.00");
    }

    void UpdateSkewValue(float value)
    {
        if (skewValueText != null)
            skewValueText.text = value.ToString("0.00");
    }
}
