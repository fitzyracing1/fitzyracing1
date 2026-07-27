using UnityEngine;

public class ProjectDetailsUI : MonoBehaviour
{
    [Header("UI Elements")]
    public GameObject detailsPanel;

    [Header("Settings")]
    public KeyCode closeKey = KeyCode.Escape;
    public float displayDuration = 5f;

    private CodingProject currentProject;
    private float displayTimer = 0f;

    void Start()
    {
        if (detailsPanel != null)
        {
            detailsPanel.SetActive(false);
        }
    }

    void Update()
    {
        if (detailsPanel != null && detailsPanel.activeSelf)
        {
            if (SimpleInput.GetInteract())
            {
                HideProject();
            }

            displayTimer -= Time.unscaledDeltaTime;
            if (displayTimer <= 0f)
            {
                HideProject();
            }
        }
    }

    public void ShowProject(CodingProject project)
    {
        if (project == null) return;

        currentProject = project;
        displayTimer = displayDuration;

        // Display project info in console (can be replaced with 3D text or UI later)
        Debug.Log("===========================================");
        Debug.Log($"PROJECT: {project.projectName}");
        Debug.Log($"Description: {project.description}");
        Debug.Log($"Language: {project.language}");
        Debug.Log($"GitHub: {project.githubUrl}");
        Debug.Log("===========================================");

        if (detailsPanel != null)
        {
            detailsPanel.SetActive(true);
        }

        // Pause game
        Time.timeScale = 0f;
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }

    public void HideProject()
    {
        if (detailsPanel != null)
        {
            detailsPanel.SetActive(false);
        }

        currentProject = null;

        // Resume game
        Time.timeScale = 1f;
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    public void OpenGitHub()
    {
        if (currentProject != null && !string.IsNullOrEmpty(currentProject.githubUrl))
        {
            Application.OpenURL(currentProject.githubUrl);
        }
    }
}
