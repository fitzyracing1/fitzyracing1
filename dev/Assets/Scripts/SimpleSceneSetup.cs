using UnityEngine;

public class SimpleSceneSetup : MonoBehaviour
{
    [Header("Setup Options")]
    public bool createFloor = true;
    public bool createPlayer = true;
    public bool createCamera = true;
    public bool createLighting = true;
    public bool createApartmentBuilding = true;

    [Header("Player Settings")]
    public Vector3 playerStartPosition = new Vector3(0f, 1f, -5f);

    void Start()
    {
        SetupScene();
    }

    void SetupScene()
    {
        Debug.Log("Setting up scene...");

        if (createFloor)
        {
            CreateFloor();
        }

        if (createPlayer)
        {
            CreatePlayer();
        }

        if (createCamera)
        {
            SetupCamera();
        }

        if (createLighting)
        {
            SetupLighting();
        }

        if (createApartmentBuilding)
        {
            CreateApartmentBuilding();
        }

        Debug.Log("Scene setup complete! Use WASD to move, Space to jump, E to interact with doors and books.");
    }

    void CreateFloor()
    {
        GameObject floor = GameObject.Find("Floor");
        if (floor == null)
        {
            floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "Floor";
            floor.transform.position = Vector3.zero;
            floor.transform.localScale = new Vector3(10f, 1f, 10f);
            
            Renderer renderer = floor.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = new Color(0.8f, 0.8f, 0.8f);
            }
            
            Debug.Log("Created floor");
        }
    }

    void CreatePlayer()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
        {
            player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            player.name = "Player";
            player.tag = "Player";
            player.transform.position = playerStartPosition;

            // Add Rigidbody
            Rigidbody rb = player.GetComponent<Rigidbody>();
            if (rb == null)
            {
                rb = player.AddComponent<Rigidbody>();
            }
            rb.mass = 1f;
            rb.linearDamping = 0f;
            rb.angularDamping = 0.05f;
            rb.constraints = RigidbodyConstraints.FreezeRotation;

            // Add PlayerController
            PlayerController controller = player.GetComponent<PlayerController>();
            if (controller == null)
            {
                controller = player.AddComponent<PlayerController>();
            }

            // Create ground check
            GameObject groundCheck = new GameObject("GroundCheck");
            groundCheck.transform.parent = player.transform;
            groundCheck.transform.localPosition = new Vector3(0f, -1f, 0f);
            controller.groundCheck = groundCheck.transform;
            controller.groundLayer = LayerMask.GetMask("Default");

            // Set player color
            Renderer renderer = player.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = Color.blue;
            }

            Debug.Log("Created player at " + playerStartPosition);
        }
    }

    void SetupCamera()
    {
        Camera mainCam = Camera.main;
        if (mainCam == null)
        {
            GameObject camObj = new GameObject("Main Camera");
            mainCam = camObj.AddComponent<Camera>();
            camObj.tag = "MainCamera";
        }

        // Add CameraFollow if player exists
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            CameraFollow camFollow = mainCam.GetComponent<CameraFollow>();
            if (camFollow == null)
            {
                camFollow = mainCam.gameObject.AddComponent<CameraFollow>();
            }
            camFollow.target = player.transform;
            camFollow.offset = new Vector3(0f, 3f, -8f);
            camFollow.smoothSpeed = 0.125f;
            
            Debug.Log("Setup camera to follow player");
        }
    }

    void SetupLighting()
    {
        Light directionalLight = FindFirstObjectByType<Light>();
        if (directionalLight == null)
        {
            GameObject lightObj = new GameObject("Directional Light");
            directionalLight = lightObj.AddComponent<Light>();
            directionalLight.type = LightType.Directional;
            lightObj.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            
            Debug.Log("Created directional light");
        }
    }

    void CreateApartmentBuilding()
    {
        // Check if building already exists
        ApartmentBuilding existingBuilding = FindFirstObjectByType<ApartmentBuilding>();
        if (existingBuilding != null)
        {
            Debug.Log("Apartment building already exists");
            return;
        }

        // Create building container
        GameObject buildingObj = new GameObject("ApartmentBuilding");
        buildingObj.transform.position = new Vector3(10f, 0f, 0f);
        
        ApartmentBuilding building = buildingObj.AddComponent<ApartmentBuilding>();
        building.numberOfFloors = 3;
        building.apartmentsPerFloor = 2;
        building.floorHeight = 4f;
        building.apartmentWidth = 6f;

        // Create simple apartment prefab
        GameObject apartmentPrefab = CreateApartmentPrefab();
        building.apartmentPrefab = apartmentPrefab;

        Debug.Log("Created apartment building - it will generate on its next Start()");
        
        // Note: The building will generate apartments in its Start() method
    }

    GameObject CreateApartmentPrefab()
    {
        GameObject apt = new GameObject("ApartmentPrefab");
        
        // Add apartment script
        Apartment apartmentScript = apt.AddComponent<Apartment>();
        
        // Create room walls (visual representation)
        GameObject walls = GameObject.CreatePrimitive(PrimitiveType.Cube);
        walls.name = "Walls";
        walls.transform.parent = apt.transform;
        walls.transform.localPosition = Vector3.zero;
        walls.transform.localScale = new Vector3(5f, 3f, 5f);
        
        Renderer wallRenderer = walls.GetComponent<Renderer>();
        if (wallRenderer != null)
        {
            wallRenderer.material.color = new Color(0.9f, 0.9f, 0.8f, 0.5f);
        }
        
        // Remove collider so player can walk through (temporary)
        Collider wallCollider = walls.GetComponent<Collider>();
        if (wallCollider != null)
        {
            Destroy(wallCollider);
        }

        // Create spawn point
        GameObject spawnPoint = new GameObject("SpawnPoint");
        spawnPoint.transform.parent = apt.transform;
        spawnPoint.transform.localPosition = new Vector3(0f, 0.5f, 0f);
        apartmentScript.spawnPoint = spawnPoint.transform;

        // Create door
        GameObject door = GameObject.CreatePrimitive(PrimitiveType.Cube);
        door.name = "Door";
        door.transform.parent = apt.transform;
        door.transform.localPosition = new Vector3(2.5f, 0.5f, 0f);
        door.transform.localScale = new Vector3(0.2f, 2f, 1f);
        
        Renderer doorRenderer = door.GetComponent<Renderer>();
        if (doorRenderer != null)
        {
            doorRenderer.material.color = new Color(0.6f, 0.3f, 0.1f);
        }

        DoorController doorController = door.AddComponent<DoorController>();
        doorController.doorPivot = door.transform;
        apartmentScript.doorController = doorController;

        // Create bookshelf
        GameObject bookshelfObj = new GameObject("Bookshelf");
        bookshelfObj.transform.parent = apt.transform;
        bookshelfObj.transform.localPosition = new Vector3(-2f, 1f, 2f);
        
        Bookshelf bookshelf = bookshelfObj.AddComponent<Bookshelf>();
        bookshelf.shelfName = "Coding Projects";
        bookshelf.maxBooks = 5;
        
        // Create book slots
        Transform[] slots = new Transform[5];
        for (int i = 0; i < 5; i++)
        {
            GameObject slot = new GameObject($"Slot_{i}");
            slot.transform.parent = bookshelfObj.transform;
            slot.transform.localPosition = new Vector3(i * 0.3f, 0f, 0f);
            slots[i] = slot.transform;
        }
        bookshelf.bookSlots = slots;

        // Add sample projects
        bookshelf.projects.Add(new CodingProject
        {
            projectId = "unity-apartments",
            projectName = "Unity Apartments",
            description = "An interactive apartment building with coding project displays",
            language = "C#",
            githubUrl = "https://github.com/yourusername/unity-apartments",
            bookColor = Color.blue
        });

        bookshelf.projects.Add(new CodingProject
        {
            projectId = "portfolio-3d",
            projectName = "3D Portfolio",
            description = "A 3D virtual portfolio experience",
            language = "C#",
            githubUrl = "https://github.com/yourusername/portfolio-3d",
            bookColor = Color.green
        });

        return apt;
    }
}
