using UnityEngine;
using UnityEngine.XR;

[DefaultExecutionOrder(-100)]
public class VRSceneSetup : MonoBehaviour
{
    [Header("VR Mode")]
    public bool enableVRMode = false;

    [Header("Scene Setup")]
    public bool createFloor = true;
    public bool createPlayer = true;
    public bool createLighting = true;
    public bool createApartmentBuilding = true;

    [Header("Player Settings")]
    public Vector3 playerStartPosition = new Vector3(0f, 0f, -5f);

    private static bool hasSetup = false;

    void Awake()
    {
        if (hasSetup) return;
        hasSetup = true;

        if (enableVRMode)
        {
            InitializeVR();
        }

        SetupScene();
    }

    void InitializeVR()
    {
        // Enable XR
        XRSettings.enabled = true;
        Debug.Log("VR Mode Enabled for Quest");
    }

    void SetupScene()
    {
        Debug.Log("Setting up VR scene...");

        if (createFloor)
        {
            CreateFloor();
        }

        if (createPlayer)
        {
            if (enableVRMode)
            {
                CreateVRPlayer();
            }
            else
            {
                CreateDesktopPlayer();
            }
        }

        if (createLighting)
        {
            SetupLighting();
        }

        if (createApartmentBuilding)
        {
            CreateApartmentBuilding();
        }

        Debug.Log("VR Scene setup complete! Use left thumbstick to move, right thumbstick to turn, trigger to interact.");
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
        }
    }

    void CreateVRPlayer()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
        {
            player = new GameObject("VRPlayer");
            player.tag = "Player";
            player.transform.position = playerStartPosition;

            // Add VR player controller
            VRPlayerController vrController = player.AddComponent<VRPlayerController>();
            vrController.moveSpeed = 3f;
            vrController.enableSmoothLocomotion = true;
            vrController.enableSnapTurn = true;

            // Create camera rig
            GameObject cameraRig = new GameObject("CameraRig");
            cameraRig.transform.parent = player.transform;
            cameraRig.transform.localPosition = Vector3.zero;
            vrController.cameraRig = cameraRig.transform;

            // Setup main camera for VR
            Camera mainCam = Camera.main;
            if (mainCam == null)
            {
                GameObject camObj = new GameObject("Main Camera");
                mainCam = camObj.AddComponent<Camera>();
                camObj.tag = "MainCamera";
            }
            
            mainCam.transform.parent = cameraRig.transform;
            mainCam.transform.localPosition = new Vector3(0f, 1.6f, 0f);
            mainCam.transform.localRotation = Quaternion.identity;
            vrController.headTransform = mainCam.transform;

            // Create left hand
            GameObject leftHand = new GameObject("LeftHand");
            leftHand.transform.parent = cameraRig.transform;
            leftHand.transform.localPosition = new Vector3(-0.2f, 1.2f, 0.3f);
            vrController.leftHandTransform = leftHand.transform;

            VRInteractor leftInteractor = leftHand.AddComponent<VRInteractor>();
            leftInteractor.isLeftHand = true;
            leftInteractor.handNode = XRNode.LeftHand;
            leftInteractor.rayLength = 10f;

            // Create left hand visual
            GameObject leftHandVisual = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            leftHandVisual.name = "LeftHandVisual";
            leftHandVisual.transform.parent = leftHand.transform;
            leftHandVisual.transform.localPosition = Vector3.zero;
            leftHandVisual.transform.localScale = Vector3.one * 0.1f;
            leftHandVisual.GetComponent<Renderer>().material.color = Color.blue;
            Destroy(leftHandVisual.GetComponent<Collider>());

            // Create right hand
            GameObject rightHand = new GameObject("RightHand");
            rightHand.transform.parent = cameraRig.transform;
            rightHand.transform.localPosition = new Vector3(0.2f, 1.2f, 0.3f);
            vrController.rightHandTransform = rightHand.transform;

            VRInteractor rightInteractor = rightHand.AddComponent<VRInteractor>();
            rightInteractor.isLeftHand = false;
            rightInteractor.handNode = XRNode.RightHand;
            rightInteractor.rayLength = 10f;

            // Create right hand visual
            GameObject rightHandVisual = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            rightHandVisual.name = "RightHandVisual";
            rightHandVisual.transform.parent = rightHand.transform;
            rightHandVisual.transform.localPosition = Vector3.zero;
            rightHandVisual.transform.localScale = Vector3.one * 0.1f;
            rightHandVisual.GetComponent<Renderer>().material.color = Color.red;
            Destroy(rightHandVisual.GetComponent<Collider>());

            Debug.Log("Created VR player");
        }
    }

    void CreateDesktopPlayer()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
        {
            player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            player.name = "Player";
            player.tag = "Player";
            player.transform.position = playerStartPosition;

            Rigidbody rb = player.AddComponent<Rigidbody>();
            rb.mass = 1f;
            rb.linearDamping = 0f;
            rb.constraints = RigidbodyConstraints.FreezeRotation;

            PlayerController controller = player.AddComponent<PlayerController>();

            GameObject groundCheck = new GameObject("GroundCheck");
            groundCheck.transform.parent = player.transform;
            groundCheck.transform.localPosition = new Vector3(0f, -1f, 0f);
            controller.groundCheck = groundCheck.transform;

            player.GetComponent<Renderer>().material.color = Color.blue;

            Debug.Log("Created desktop player");
        }

        // Always setup camera separately
        SetupDesktopCamera();
    }

    void SetupDesktopCamera()
    {
        Camera mainCam = Camera.main;
        if (mainCam == null)
        {
            GameObject camObj = new GameObject("Main Camera");
            mainCam = camObj.AddComponent<Camera>();
            camObj.tag = "MainCamera";
            camObj.AddComponent<AudioListener>();
            Debug.Log("Created main camera");
        }

        // Remove any CameraFollow that might exist
        CameraFollow existingFollow = mainCam.GetComponent<CameraFollow>();
        if (existingFollow != null)
        {
            Destroy(existingFollow);
        }

        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            CameraFollow camFollow = mainCam.gameObject.AddComponent<CameraFollow>();
            camFollow.target = player.transform;
            camFollow.offset = new Vector3(0f, 3f, -8f);
            camFollow.smoothSpeed = 0.125f;
            Debug.Log("Camera following player");
        }
        else
        {
            // No player, just position camera
            mainCam.transform.position = new Vector3(0f, 2f, -5f);
            mainCam.transform.rotation = Quaternion.Euler(10f, 0f, 0f);
            Debug.Log("Camera positioned, no player to follow");
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
        }
    }

    void CreateApartmentBuilding()
    {
        ApartmentBuilding existingBuilding = FindFirstObjectByType<ApartmentBuilding>();
        if (existingBuilding != null) return;

        GameObject buildingObj = new GameObject("ApartmentBuilding");
        buildingObj.transform.position = new Vector3(10f, 0f, 0f);
        
        ApartmentBuilding building = buildingObj.AddComponent<ApartmentBuilding>();
        building.numberOfFloors = 3;
        building.apartmentsPerFloor = 2;
        building.floorHeight = 4f;
        building.apartmentWidth = 6f;
        building.apartmentPrefab = CreateApartmentPrefab();
    }

    GameObject CreateApartmentPrefab()
    {
        GameObject apt = new GameObject("ApartmentPrefab");
        Apartment apartmentScript = apt.AddComponent<Apartment>();
        
        GameObject walls = GameObject.CreatePrimitive(PrimitiveType.Cube);
        walls.name = "Walls";
        walls.transform.parent = apt.transform;
        walls.transform.localPosition = Vector3.zero;
        walls.transform.localScale = new Vector3(5f, 3f, 5f);
        walls.GetComponent<Renderer>().material.color = new Color(0.9f, 0.9f, 0.8f, 0.5f);
        Destroy(walls.GetComponent<Collider>());

        GameObject spawnPoint = new GameObject("SpawnPoint");
        spawnPoint.transform.parent = apt.transform;
        spawnPoint.transform.localPosition = new Vector3(0f, 0.5f, 0f);
        apartmentScript.spawnPoint = spawnPoint.transform;

        GameObject door = GameObject.CreatePrimitive(PrimitiveType.Cube);
        door.name = "Door";
        door.transform.parent = apt.transform;
        door.transform.localPosition = new Vector3(2.5f, 0.5f, 0f);
        door.transform.localScale = new Vector3(0.2f, 2f, 1f);
        door.GetComponent<Renderer>().material.color = new Color(0.6f, 0.3f, 0.1f);

        DoorController doorController = door.AddComponent<DoorController>();
        doorController.doorPivot = door.transform;
        apartmentScript.doorController = doorController;

        GameObject bookshelfObj = new GameObject("Bookshelf");
        bookshelfObj.transform.parent = apt.transform;
        bookshelfObj.transform.localPosition = new Vector3(-2f, 1f, 2f);
        
        Bookshelf bookshelf = bookshelfObj.AddComponent<Bookshelf>();
        bookshelf.shelfName = "Coding Projects";
        bookshelf.maxBooks = 5;
        
        Transform[] slots = new Transform[5];
        for (int i = 0; i < 5; i++)
        {
            GameObject slot = new GameObject($"Slot_{i}");
            slot.transform.parent = bookshelfObj.transform;
            slot.transform.localPosition = new Vector3(i * 0.3f, 0f, 0f);
            slots[i] = slot.transform;
        }
        bookshelf.bookSlots = slots;

        bookshelf.projects.Add(new CodingProject
        {
            projectId = "unity-apartments",
            projectName = "Unity Apartments VR",
            description = "An interactive VR apartment building with coding project displays",
            language = "C#",
            githubUrl = "https://github.com/yourusername/unity-apartments-vr",
            bookColor = Color.blue
        });

        bookshelf.projects.Add(new CodingProject
        {
            projectId = "portfolio-3d",
            projectName = "3D VR Portfolio",
            description = "A virtual reality portfolio experience for Quest",
            language = "C#",
            githubUrl = "https://github.com/yourusername/portfolio-vr",
            bookColor = Color.green
        });

        return apt;
    }
}
