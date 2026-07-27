using UnityEngine;
using UnityEngine.Events;

public class ProjectBook : MonoBehaviour
{
    [Header("Project Data")]
    public CodingProject project;
    public Bookshelf parentShelf;

    [Header("Interaction Settings")]
    public float interactionDistance = 3f;
    public KeyCode interactKey = KeyCode.E;

    [Header("Visual Settings")]
    public bool highlightOnHover = true;
    public Color highlightColor = Color.yellow;

    [Header("Events")]
    public UnityEvent<CodingProject> onProjectSelected;

    private Renderer bookRenderer;
    private Color originalColor;
    private bool isPlayerNearby = false;
    private GameObject nearbyPlayer;

    void Start()
    {
        bookRenderer = GetComponent<Renderer>();
        if (bookRenderer != null && project != null)
        {
            originalColor = project.bookColor;
            bookRenderer.material.color = originalColor;
        }
    }

    void Update()
    {
        CheckPlayerProximity();

        if (isPlayerNearby && SimpleInput.GetInteract())
        {
            SelectProject();
        }
    }

    void CheckPlayerProximity()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null) return;

        float distance = Vector3.Distance(transform.position, player.transform.position);
        bool wasNearby = isPlayerNearby;
        isPlayerNearby = distance <= interactionDistance;

        if (isPlayerNearby && !wasNearby)
        {
            OnPlayerEnterRange(player);
        }
        else if (!isPlayerNearby && wasNearby)
        {
            OnPlayerExitRange();
        }
    }

    void OnPlayerEnterRange(GameObject player)
    {
        nearbyPlayer = player;
        
        if (highlightOnHover && bookRenderer != null)
        {
            bookRenderer.material.color = highlightColor;
        }

        if (project != null)
        {
            Debug.Log($"Press {interactKey} to view: {project.projectName}");
        }
    }

    void OnPlayerExitRange()
    {
        nearbyPlayer = null;

        if (highlightOnHover && bookRenderer != null)
        {
            bookRenderer.material.color = originalColor;
        }
    }

    public void SelectProject()
    {
        if (project == null) return;

        Debug.Log($"=== Project: {project.projectName} ===");
        Debug.Log($"Description: {project.description}");
        Debug.Log($"Language: {project.language}");
        Debug.Log($"GitHub: {project.githubUrl}");

        onProjectSelected?.Invoke(project);

        // You can open a UI panel here to show more details
        ProjectDetailsUI detailsUI = FindFirstObjectByType<ProjectDetailsUI>();
        if (detailsUI != null)
        {
            detailsUI.ShowProject(project);
        }
    }

    void OnDrawGizmosSelected()
    {
        // Draw interaction range
        Gizmos.color = new Color(0f, 1f, 0f, 0.3f);
        Gizmos.DrawWireSphere(transform.position, interactionDistance);
    }

    // Public method to update project data
    public void SetProject(CodingProject newProject)
    {
        project = newProject;
        
        if (bookRenderer != null && project != null)
        {
            originalColor = project.bookColor;
            bookRenderer.material.color = originalColor;
        }

        gameObject.name = project != null ? project.projectName : "Empty Book";
    }
}
