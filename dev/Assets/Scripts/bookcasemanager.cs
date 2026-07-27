using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class ProjectData
{
    public string id;
    public string title;
    public string description;
    public Texture2D thumbnail;
}

public class BookcaseManager : MonoBehaviour
{
    public Transform[] shelfSlots;            // assign slot Transforms in inspector
    public GameObject projectCardPrefab;     // prefab with ProjectCard script

    [Header("Sample data - can be replaced with JSON loader")]
    public List<ProjectData> sampleProjects = new List<ProjectData>();

    void Start()
    {
        PopulateShelves();
    }

    public void PopulateShelves()
    {
        int i = 0;
        foreach (var proj in sampleProjects)
        {
            if (i >= shelfSlots.Length) break;
            var slot = shelfSlots[i];
            var obj = Instantiate(projectCardPrefab, slot.position, slot.rotation, slot);
            obj.transform.localScale = Vector3.one; // adjust if needed

            var card = obj.GetComponent<ProjectCard>();
            if (card != null)
            {
                card.Populate(proj.thumbnail, proj.title, proj.id, proj.description);
                // Hook up selection to show details:
                card.onSelected.AddListener(() => ShowProjectDetails(proj));
            }

            i++;
        }
    }

    void ShowProjectDetails(ProjectData proj)
    {
        // Show your world-space UI panel or a popup in front of the user.
        // Implement the UI controller to receive ProjectData and render.
        Debug.Log("Show details for: " + proj.title);
    }

    // Optional: load projects from Resources/JSON at runtime
    // public void LoadFromJson(string jsonPath) { ... }
}
