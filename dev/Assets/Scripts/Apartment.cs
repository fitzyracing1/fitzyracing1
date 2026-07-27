using UnityEngine;
using System.Collections.Generic;

public class Apartment : MonoBehaviour
{
    [Header("Apartment Info")]
    public int floorNumber;
    public int unitNumber;
    public string apartmentName;

    [Header("Room Settings")]
    public Transform spawnPoint;
    public List<Bookshelf> bookshelves = new List<Bookshelf>();

    [Header("Door Settings")]
    public DoorController doorController;
    public bool isLocked = false;

    void Start()
    {
        // Find all bookshelves in this apartment
        Bookshelf[] foundShelves = GetComponentsInChildren<Bookshelf>();
        bookshelves.AddRange(foundShelves);

        // Setup door reference
        if (doorController != null)
        {
            doorController.apartment = this;
        }
    }

    public void EnterApartment(GameObject player)
    {
        if (isLocked)
        {
            Debug.Log($"{apartmentName} is locked!");
            return;
        }

        Debug.Log($"Entered {apartmentName}");

        // Teleport player to spawn point if available
        if (spawnPoint != null && player != null)
        {
            player.transform.position = spawnPoint.position;
            player.transform.rotation = spawnPoint.rotation;
        }
    }

    public void ExitApartment(GameObject player)
    {
        Debug.Log($"Exited {apartmentName}");
    }

    public void AddBookshelf(Bookshelf bookshelf)
    {
        if (!bookshelves.Contains(bookshelf))
        {
            bookshelves.Add(bookshelf);
        }
    }

    public int GetTotalProjects()
    {
        int total = 0;
        foreach (Bookshelf shelf in bookshelves)
        {
            total += shelf.GetBookCount();
        }
        return total;
    }
}
