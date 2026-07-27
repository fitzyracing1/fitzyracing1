using UnityEngine;
using UnityEngine.Events;

public class DoorController : MonoBehaviour
{
    [Header("Door Settings")]
    public Apartment apartment;
    public Transform doorPivot;
    public float openAngle = 90f;
    public float doorSpeed = 2f;

    [Header("Interaction")]
    public float interactionDistance = 5f;
    public KeyCode interactKey = KeyCode.E;
    public bool isOpen = false;

    [Header("Events")]
    public UnityEvent onDoorOpened;
    public UnityEvent onDoorClosed;

    private Quaternion closedRotation;
    private Quaternion openRotation;
    private bool isPlayerNearby = false;
    private bool isAnimating = false;

    void Start()
    {
        if (doorPivot == null)
            doorPivot = transform;

        closedRotation = doorPivot.rotation;
        openRotation = closedRotation * Quaternion.Euler(0f, openAngle, 0f);
    }

    void Update()
    {
        // Desktop mode
        CheckPlayerProximity();

        if (isPlayerNearby && SimpleInput.GetInteract() && !isAnimating)
        {
            Debug.Log("[DOOR] E key pressed near door!");
            if (apartment != null && apartment.isLocked && !isOpen)
            {
                Debug.Log($"[DOOR] Door is locked!");
                return;
            }

            ToggleDoor();
        }

        AnimateDoor();
    }

    void CheckPlayerProximity()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
        {
            isPlayerNearby = false;
            return;
        }

        float distance = Vector3.Distance(transform.position, player.transform.position);
        bool wasNearby = isPlayerNearby;
        isPlayerNearby = distance <= interactionDistance;

        if (isPlayerNearby && !wasNearby && !isAnimating)
        {
            string status = (apartment != null && apartment.isLocked) ? "Locked" : (isOpen ? "Close" : "Open");
            Debug.Log($"[DOOR] Near door! Press {interactKey} to {status} (distance: {distance:F1})");
        }
    }

    public void ToggleDoor()
    {
        if (apartment != null && apartment.isLocked && !isOpen)
        {
            Debug.Log($"Door is locked!");
            return;
        }

        isOpen = !isOpen;
        isAnimating = true;

        if (isOpen)
        {
            Debug.Log("Opening door...");
            onDoorOpened?.Invoke();
        }
        else
        {
            Debug.Log("Closing door...");
            onDoorClosed?.Invoke();
        }
    }

    void AnimateDoor()
    {
        if (!isAnimating) return;

        Quaternion targetRotation = isOpen ? openRotation : closedRotation;
        doorPivot.rotation = Quaternion.Lerp(doorPivot.rotation, targetRotation, Time.deltaTime * doorSpeed);

        if (Quaternion.Angle(doorPivot.rotation, targetRotation) < 0.1f)
        {
            doorPivot.rotation = targetRotation;
            isAnimating = false;
        }
    }

    public void OpenDoor()
    {
        if (!isOpen && !isAnimating)
        {
            isOpen = true;
            isAnimating = true;
            onDoorOpened?.Invoke();
        }
    }

    public void CloseDoor()
    {
        if (isOpen && !isAnimating)
        {
            isOpen = false;
            isAnimating = true;
            onDoorClosed?.Invoke();
        }
    }

    public void LockDoor()
    {
        if (apartment != null)
        {
            apartment.isLocked = true;
            Debug.Log("Door locked");
        }
    }

    public void UnlockDoor()
    {
        if (apartment != null)
        {
            apartment.isLocked = false;
            Debug.Log("Door unlocked");
        }
    }

    void OnDrawGizmosSelected()
    {
        // Draw interaction range
        Gizmos.color = Color.green;
        Gizmos.DrawWireSphere(transform.position, interactionDistance);

        // Draw door swing arc
        if (doorPivot != null)
        {
            Gizmos.color = Color.blue;
            Vector3 forward = doorPivot.forward;
            Vector3 right = doorPivot.right;
            
            for (int i = 0; i <= 10; i++)
            {
                float angle = (openAngle / 10) * i;
                Vector3 direction = Quaternion.Euler(0f, angle, 0f) * forward;
                Gizmos.DrawLine(doorPivot.position, doorPivot.position + direction * 1.5f);
            }
        }
    }
}
