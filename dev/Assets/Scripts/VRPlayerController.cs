using UnityEngine;
using UnityEngine.XR;

public class VRPlayerController : MonoBehaviour
{
    [Header("VR Settings")]
    public Transform cameraRig;
    public Transform headTransform;
    public Transform leftHandTransform;
    public Transform rightHandTransform;

    [Header("Movement Settings")]
    public float moveSpeed = 3f;
    public float rotationSpeed = 45f;
    public bool enableSmoothLocomotion = true;
    public bool enableSnapTurn = true;
    public float snapTurnAngle = 30f;

    [Header("Input Settings")]
    public XRNode leftHandNode = XRNode.LeftHand;
    public XRNode rightHandNode = XRNode.RightHand;

    private CharacterController characterController;
    private Vector2 leftThumbstick;
    private Vector2 rightThumbstick;
    private bool wasSnapTurning = false;

    void Start()
    {
        characterController = GetComponent<CharacterController>();
        if (characterController == null)
        {
            characterController = gameObject.AddComponent<CharacterController>();
            characterController.height = 1.8f;
            characterController.radius = 0.3f;
            characterController.center = new Vector3(0f, 0.9f, 0f);
        }

        SetupVRRig();
    }

    void SetupVRRig()
    {
        if (cameraRig == null)
        {
            GameObject rigObj = new GameObject("CameraRig");
            rigObj.transform.parent = transform;
            rigObj.transform.localPosition = Vector3.zero;
            cameraRig = rigObj.transform;
        }

        if (headTransform == null)
        {
            Camera mainCam = Camera.main;
            if (mainCam != null)
            {
                headTransform = mainCam.transform;
                headTransform.parent = cameraRig;
                headTransform.localPosition = new Vector3(0f, 1.6f, 0f);
            }
        }

        // Create hand transforms if not assigned
        if (leftHandTransform == null)
        {
            GameObject leftHand = new GameObject("LeftHand");
            leftHand.transform.parent = cameraRig;
            leftHandTransform = leftHand.transform;
        }

        if (rightHandTransform == null)
        {
            GameObject rightHand = new GameObject("RightHand");
            rightHand.transform.parent = cameraRig;
            rightHandTransform = rightHand.transform;
        }
    }

    void Update()
    {
        GetVRInput();

        if (enableSmoothLocomotion)
        {
            HandleMovement();
        }

        if (enableSnapTurn)
        {
            HandleSnapTurn();
        }

        // Keep camera rig centered on character
        if (headTransform != null)
        {
            Vector3 headOffset = headTransform.localPosition;
            headOffset.y = 0f;
            cameraRig.localPosition = -headOffset;
        }
    }

    void GetVRInput()
    {
        // Get left thumbstick
        InputDevice leftDevice = InputDevices.GetDeviceAtXRNode(leftHandNode);
        leftDevice.TryGetFeatureValue(CommonUsages.primary2DAxis, out leftThumbstick);

        // Get right thumbstick
        InputDevice rightDevice = InputDevices.GetDeviceAtXRNode(rightHandNode);
        rightDevice.TryGetFeatureValue(CommonUsages.primary2DAxis, out rightThumbstick);
    }

    void HandleMovement()
    {
        if (characterController == null || headTransform == null) return;

        // Get forward direction based on head orientation
        Vector3 forward = headTransform.forward;
        Vector3 right = headTransform.right;

        // Flatten to horizontal plane
        forward.y = 0f;
        right.y = 0f;
        forward.Normalize();
        right.Normalize();

        // Calculate movement direction
        Vector3 moveDirection = (forward * leftThumbstick.y + right * leftThumbstick.x) * moveSpeed;

        // Apply gravity
        moveDirection.y = -9.81f;

        // Move character
        characterController.Move(moveDirection * Time.deltaTime);
    }

    void HandleSnapTurn()
    {
        float turnInput = rightThumbstick.x;

        if (Mathf.Abs(turnInput) > 0.7f && !wasSnapTurning)
        {
            float turnAmount = turnInput > 0 ? snapTurnAngle : -snapTurnAngle;
            transform.Rotate(0f, turnAmount, 0f);
            wasSnapTurning = true;
        }
        else if (Mathf.Abs(turnInput) < 0.3f)
        {
            wasSnapTurning = false;
        }
    }

    public bool IsTriggerPressed(bool leftHand)
    {
        XRNode node = leftHand ? leftHandNode : rightHandNode;
        InputDevice device = InputDevices.GetDeviceAtXRNode(node);
        
        bool triggerPressed;
        device.TryGetFeatureValue(CommonUsages.triggerButton, out triggerPressed);
        
        return triggerPressed;
    }

    public bool IsGripPressed(bool leftHand)
    {
        XRNode node = leftHand ? leftHandNode : rightHandNode;
        InputDevice device = InputDevices.GetDeviceAtXRNode(node);
        
        bool gripPressed;
        device.TryGetFeatureValue(CommonUsages.gripButton, out gripPressed);
        
        return gripPressed;
    }

    public bool IsPrimaryButtonPressed(bool leftHand)
    {
        XRNode node = leftHand ? leftHandNode : rightHandNode;
        InputDevice device = InputDevices.GetDeviceAtXRNode(node);
        
        bool buttonPressed;
        device.TryGetFeatureValue(CommonUsages.primaryButton, out buttonPressed);
        
        return buttonPressed;
    }
}
