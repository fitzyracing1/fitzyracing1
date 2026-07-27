using UnityEngine;
using UnityEngine.Events;
using TMPro;
using UnityEngine.UI;

[RequireComponent(typeof(Collider))]
public class ProjectCard : MonoBehaviour
{
    [Header("Visuals")]
    public Renderer thumbnailRenderer;
    public TextMeshPro titleText;

    [Header("Data")]
    public string projectId;
    public string title;
    [TextArea(3,8)]
    public string description;

    public UnityEvent onSelected;

    // Call to populate visual data
    public void Populate(Texture2D thumbnail, string titleTextStr, string projectIdStr, string desc)
    {
        if (thumbnailRenderer != null)
        {
            thumbnailRenderer.material.mainTexture = thumbnail;
        }
        if (titleText != null)
            titleText.text = titleTextStr;
        projectId = projectIdStr;
        title = titleTextStr;
        description = desc;
    }

    // This should be wired to XR Interaction Toolkit "OnSelectEntered" or to a simple pointer click.
    public void OnSelect()
    {
        // raise event to show details
        onSelected?.Invoke();
    }
}
