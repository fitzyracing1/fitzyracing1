using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public class CodingProject
{
    public string projectId;
    public string projectName;
    public string description;
    public string githubUrl;
    public string language;
    public Sprite icon;
    public Color bookColor = Color.white;
}

public class Bookshelf : MonoBehaviour
{
    [Header("Bookshelf Settings")]
    public string shelfName = "Coding Projects";
    public int maxBooks = 10;

    [Header("Book Placement")]
    public Transform[] bookSlots;
    public GameObject bookPrefab;

    [Header("Projects")]
    public List<CodingProject> projects = new List<CodingProject>();

    private List<GameObject> spawnedBooks = new List<GameObject>();

    void Start()
    {
        if (bookSlots == null || bookSlots.Length == 0)
        {
            Debug.LogWarning($"No book slots assigned for bookshelf: {shelfName}");
        }

        DisplayProjects();
    }

    public void AddProject(CodingProject project)
    {
        if (projects.Count >= maxBooks)
        {
            Debug.LogWarning($"Bookshelf {shelfName} is full!");
            return;
        }

        projects.Add(project);
        DisplayProjects();
        Debug.Log($"Added project '{project.projectName}' to {shelfName}");
    }

    public void RemoveProject(string projectId)
    {
        CodingProject project = projects.Find(p => p.projectId == projectId);
        if (project != null)
        {
            projects.Remove(project);
            DisplayProjects();
            Debug.Log($"Removed project '{project.projectName}' from {shelfName}");
        }
    }

    public void DisplayProjects()
    {
        // Clear existing books
        foreach (GameObject book in spawnedBooks)
        {
            if (book != null)
                Destroy(book);
        }
        spawnedBooks.Clear();

        // Spawn new books
        for (int i = 0; i < projects.Count && i < bookSlots.Length; i++)
        {
            if (bookSlots[i] == null) continue;

            GameObject bookObj;
            if (bookPrefab != null)
            {
                bookObj = Instantiate(bookPrefab, bookSlots[i].position, bookSlots[i].rotation, bookSlots[i]);
            }
            else
            {
                // Create a simple cube as fallback
                bookObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                bookObj.transform.position = bookSlots[i].position;
                bookObj.transform.rotation = bookSlots[i].rotation;
                bookObj.transform.parent = bookSlots[i];
                bookObj.transform.localScale = new Vector3(0.1f, 0.3f, 0.2f);
            }

            bookObj.name = projects[i].projectName;

            // Apply color to book
            Renderer renderer = bookObj.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = projects[i].bookColor;
            }

            // Add ProjectBook component
            ProjectBook bookComponent = bookObj.GetComponent<ProjectBook>();
            if (bookComponent == null)
            {
                bookComponent = bookObj.AddComponent<ProjectBook>();
            }
            bookComponent.project = projects[i];
            bookComponent.parentShelf = this;

            spawnedBooks.Add(bookObj);
        }
    }

    public int GetBookCount()
    {
        return projects.Count;
    }

    public CodingProject GetProject(string projectId)
    {
        return projects.Find(p => p.projectId == projectId);
    }

    void OnDrawGizmos()
    {
        if (bookSlots == null) return;

        Gizmos.color = Color.cyan;
        foreach (Transform slot in bookSlots)
        {
            if (slot != null)
            {
                Gizmos.DrawWireCube(slot.position, new Vector3(0.1f, 0.3f, 0.2f));
            }
        }
    }
}
