using UnityEngine;
using UnityEngine.XR;
using UnityEngine.XR.Interaction.Toolkit;

namespace VirtualOffice.VR
{
    /// <summary>
    /// Main VR controller handler for Meta Quest hand tracking
    /// </summary>
    [RequireComponent(typeof(XRController))]
    public class VRController : MonoBehaviour
    {
        [Header("Controller Settings")]
        [SerializeField] private XRNode controllerNode = XRNode.RightHand;
        [SerializeField] private InputHelpers.Button triggerButton = InputHelpers.Button.Trigger;
        [SerializeField] private InputHelpers.Button gripButton = InputHelpers.Button.Grip;

        [Header("Visual Feedback")]
        [SerializeField] private GameObject handModel;
        [SerializeField] private Material defaultMaterial;
        [SerializeField] private Material highlightMaterial;

        private XRController xrController;
        private Renderer handRenderer;
        private bool isTriggerPressed;
        private bool isGripPressed;

        private void Awake()
        {
            xrController = GetComponent<XRController>();
            
            if (handModel != null)
            {
                handRenderer = handModel.GetComponent<Renderer>();
            }
        }

        private void Update()
        {
            CheckTriggerInput();
            CheckGripInput();
            UpdateControllerPosition();
        }

        private void CheckTriggerInput()
        {
            bool triggerValue = false;
            InputHelpers.IsPressed(
                InputDevices.GetDeviceAtXRNode(controllerNode),
                triggerButton,
                out triggerValue
            );

            if (triggerValue && !isTriggerPressed)
            {
                OnTriggerPressed();
            }
            else if (!triggerValue && isTriggerPressed)
            {
                OnTriggerReleased();
            }

            isTriggerPressed = triggerValue;
        }

        private void CheckGripInput()
        {
            bool gripValue = false;
            InputHelpers.IsPressed(
                InputDevices.GetDeviceAtXRNode(controllerNode),
                gripButton,
                out gripValue
            );

            if (gripValue && !isGripPressed)
            {
                OnGripPressed();
            }
            else if (!gripValue && isGripPressed)
            {
                OnGripReleased();
            }

            isGripPressed = gripValue;
        }

        private void UpdateControllerPosition()
        {
            InputDevice device = InputDevices.GetDeviceAtXRNode(controllerNode);
            
            if (device.isValid)
            {
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
        }

        private void OnTriggerPressed()
        {
            Debug.Log($"{controllerNode} Trigger Pressed");
            SetHandHighlight(true);
        }

        private void OnTriggerReleased()
        {
            Debug.Log($"{controllerNode} Trigger Released");
            SetHandHighlight(false);
        }

        private void OnGripPressed()
        {
            Debug.Log($"{controllerNode} Grip Pressed");
        }

        private void OnGripReleased()
        {
            Debug.Log($"{controllerNode} Grip Released");
        }

        private void SetHandHighlight(bool highlight)
        {
            if (handRenderer != null)
            {
                handRenderer.material = highlight ? highlightMaterial : defaultMaterial;
            }
        }

        /// <summary>
        /// Check if trigger is currently pressed
        /// </summary>
        public bool IsTriggerPressed()
        {
            return isTriggerPressed;
        }

        /// <summary>
        /// Check if grip is currently pressed
        /// </summary>
        public bool IsGripPressed()
        {
            return isGripPressed;
        }

        /// <summary>
        /// Get the controller's current velocity
        /// </summary>
        public Vector3 GetVelocity()
        {
            Vector3 velocity = Vector3.zero;
            InputDevice device = InputDevices.GetDeviceAtXRNode(controllerNode);
            
            if (device.isValid)
            {
                device.TryGetFeatureValue(CommonUsages.deviceVelocity, out velocity);
            }

            return velocity;
        }
    }
}
