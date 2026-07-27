using UnityEngine;
using UnityEngine.XR;

public class VRInteractor : MonoBehaviour
{
    [Header("VR Hand Settings")]
    public bool isLeftHand = false;
    public XRNode handNode;

    [Header("Interaction Settings")]
    public float rayLength = 5f;
    public LayerMask interactableLayer;
    public LineRenderer pointerLine;

    [Header("Visual Feedback")]
    public GameObject handModel;
    public Color normalColor = Color.white;
    public Color hoverColor = Color.yellow;

    private VRPlayerController vrPlayer;
    private GameObject currentTarget;
    private bool wasTriggerPressed = false;

    void Start()
    {
        vrPlayer = GetComponentInParent<VRPlayerController>();
        
        handNode = isLeftHand ? XRNode.LeftHand : XRNode.RightHand;

        if (pointerLine == null)
        {
            GameObject lineObj = new GameObject("PointerLine");
            lineObj.transform.parent = transform;
            lineObj.transform.localPosition = Vector3.zero;
            pointerLine = lineObj.AddComponent<LineRenderer>();
            pointerLine.startWidth = 0.01f;
            pointerLine.endWidth = 0.01f;
            pointerLine.material = new Material(Shader.Find("Sprites/Default"));
            pointerLine.startColor = normalColor;
            pointerLine.endColor = normalColor;
        }
    }

    void Update()
    {
        UpdateHandTracking();
        PerformRaycast();
        HandleInteraction();
    }

    void UpdateHandTracking()
    {
        InputDevice device = InputDevices.GetDeviceAtXRNode(handNode);
        
        Vector3 position;
        Quaternion rotation;
        
        if (device.TryGetFeatureValue(CommonUsages.devicePosition, out position))
        {
            transform.localPosition = position;
        }

        if (device.TryGetFeatureValue(CommonUsages.deviceRotation, out rotation))
        {
            transform.localRotation = rotation;
        }
    }

    void PerformRaycast()
    {
        Ray ray = new Ray(transform.position, transform.forward);
        RaycastHit hit;

        if (Physics.Raycast(ray, out hit, rayLength, interactableLayer))
        {
            currentTarget = hit.collider.gameObject;
            
            // Update pointer line
            if (pointerLine != null)
            {
                pointerLine.SetPosition(0, transform.position);
                pointerLine.SetPosition(1, hit.point);
                pointerLine.startColor = hoverColor;
                pointerLine.endColor = hoverColor;
            }

            // Highlight object
            HighlightObject(currentTarget, true);
        }
        else
        {
            if (currentTarget != null)
            {
                HighlightObject(currentTarget, false);
            }
            currentTarget = null;

            // Update pointer line
            if (pointerLine != null)
            {
                pointerLine.SetPosition(0, transform.position);
                pointerLine.SetPosition(1, transform.position + transform.forward * rayLength);
                pointerLine.startColor = normalColor;
                pointerLine.endColor = normalColor;
            }
        }
    }

    void HandleInteraction()
    {
        if (vrPlayer == null) return;

        bool triggerPressed = vrPlayer.IsTriggerPressed(isLeftHand);

        if (triggerPressed && !wasTriggerPressed && currentTarget != null)
        {
            InteractWithObject(currentTarget);
        }

        wasTriggerPressed = triggerPressed;
    }

    void InteractWithObject(GameObject obj)
    {
        // Check for door controller
        DoorController door = obj.GetComponent<DoorController>();
        if (door != null)
        {
            door.ToggleDoor();
            return;
        }

        // Check for project book
        ProjectBook book = obj.GetComponent<ProjectBook>();
        if (book != null)
        {
            book.SelectProject();
            return;
        }

        Debug.Log($"Interacted with: {obj.name}");
    }

    void HighlightObject(GameObject obj, bool highlight)
    {
        Renderer renderer = obj.GetComponent<Renderer>();
        if (renderer != null)
        {
            if (highlight)
            {
                // Store original color and apply highlight
                renderer.material.color = hoverColor;
            }
            else
            {
                // Restore original color (simplified)
                renderer.material.color = Color.white;
            }
        }
    }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.cyan;
        Gizmos.DrawRay(transform.position, transform.forward * rayLength);
    }
}
