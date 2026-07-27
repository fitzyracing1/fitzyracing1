using UnityEngine;
using System.Collections.Generic;

public class ApartmentBuilding : MonoBehaviour
{
    [Header("Building Settings")]
    public int numberOfFloors = 5;
    public int apartmentsPerFloor = 4;
    public float floorHeight = 3f;
    public float apartmentWidth = 8f;

    [Header("Prefab References")]
    public GameObject apartmentPrefab;
    public GameObject hallwayPrefab;
    public GameObject stairsPrefab;

    [Header("Building Layout")]
    public List<Apartment> apartments = new List<Apartment>();

    void Start()
    {
        if (apartmentPrefab == null)
        {
            Debug.LogWarning("Apartment prefab not assigned! Building generation skipped.");
            return;
        }

        GenerateBuilding();
    }

    void GenerateBuilding()
    {
        apartments.Clear();

        for (int floor = 0; floor < numberOfFloors; floor++)
        {
            for (int unit = 0; unit < apartmentsPerFloor; unit++)
            {
                CreateApartment(floor, unit);
            }
        }

        Debug.Log($"Generated building with {apartments.Count} apartments across {numberOfFloors} floors");
    }

    void CreateApartment(int floor, int unit)
    {
        float yPosition = floor * floorHeight;
        float xPosition = unit * apartmentWidth;

        Vector3 position = new Vector3(xPosition, yPosition, 0f);
        
        GameObject apartmentObj = Instantiate(apartmentPrefab, position, Quaternion.identity, transform);
        apartmentObj.name = $"Apartment_{floor}_{unit}";

        Apartment apartment = apartmentObj.GetComponent<Apartment>();
        if (apartment != null)
        {
            apartment.floorNumber = floor;
            apartment.unitNumber = unit;
            apartment.apartmentName = $"Apartment {floor * apartmentsPerFloor + unit + 1}";
            apartments.Add(apartment);
        }
    }

    public Apartment GetApartment(int floor, int unit)
    {
        return apartments.Find(apt => apt.floorNumber == floor && apt.unitNumber == unit);
    }

    void OnDrawGizmos()
    {
        // Visualize building bounds
        Gizmos.color = new Color(0f, 1f, 0f, 0.3f);
        Vector3 buildingSize = new Vector3(
            apartmentWidth * apartmentsPerFloor,
            floorHeight * numberOfFloors,
            5f
        );
        Gizmos.DrawWireCube(transform.position + buildingSize / 2f, buildingSize);
    }
}
