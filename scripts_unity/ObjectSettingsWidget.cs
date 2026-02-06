using UnityEngine;
using UnityEngine.UI;

public class ObjectSettingsWidget : MonoBehaviour
{
    public Button settingsButton;
    public ObjectSettingsManager manager;
    public Transform target;

    void Awake()
    {
        if (settingsButton != null)
            settingsButton.onClick.AddListener(OnSettingsClicked);
    }

    public void Initialize(ObjectSettingsManager settingsManager, Transform targetTransform)
    {
        manager = settingsManager;
        target = targetTransform;
    }

    void OnSettingsClicked()
    {
        if (manager == null)
            return;
        manager.Show();
    }
}
