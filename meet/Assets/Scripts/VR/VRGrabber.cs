using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

namespace VirtualOffice.VR
{
    /// <summary>
    /// Handles grabbing and releasing objects in VR
    /// </summary>
    public class VRGrabber : MonoBehaviour
    {
        [Header("Grab Settings")]
        [SerializeField] private Transform grabPoint;
        [SerializeField] private float grabRadius = 0.1f;
        [SerializeField] private LayerMask grabbableLayer;
        [SerializeField] private VRController vrController;

        [Header("Physics")]
        [SerializeField] private float throwForceMultiplier = 1.5f;
        [SerializeField] private float rotationSpeed = 10f;

        private GameObject grabbedObject;
        private Rigidbody grabbedRigidbody;
        private Transform originalParent;
        private Vector3 previousPosition;
        private Quaternion previousRotation;

        private void Awake()
        {
            if (grabPoint == null)
            {
                grabPoint = transform;
            }

            if (vrController == null)
            {
                vrController = GetComponent<VRController>();
            }
        }

        private void Update()
        {
            if (vrController == null) return;

            if (vrController.IsGripPressed() && grabbedObject == null)
            {
                TryGrabObject();
            }
            else if (!vrController.IsGripPressed() && grabbedObject != null)
            {
                ReleaseObject();
            }

            if (grabbedObject != null)
            {
                UpdateGrabbedObject();
            }
        }

        private void TryGrabObject()
        {
            Collider[] hitColliders = Physics.OverlapSphere(
                grabPoint.position,
                grabRadius,
                grabbableLayer
            );

            if (hitColliders.Length > 0)
            {
                GameObject targetObject = hitColliders[0].gameObject;
                GrabObject(targetObject);
            }
        }

        private void GrabObject(GameObject obj)
        {
            grabbedObject = obj;
            grabbedRigidbody = obj.GetComponent<Rigidbody>();
            originalParent = obj.transform.parent;

            // Disable physics while holding
            if (grabbedRigidbody != null)
            {
                grabbedRigidbody.isKinematic = true;
                grabbedRigidbody.useGravity = false;
            }

            // Parent to grab point
            obj.transform.SetParent(grabPoint);

            previousPosition = grabPoint.position;
            previousRotation = grabPoint.rotation;

            Debug.Log($"Grabbed object: {obj.name}");
        }

        private void ReleaseObject()
        {
            if (grabbedObject == null) return;

            // Restore original parent
            grabbedObject.transform.SetParent(originalParent);

            // Re-enable physics
            if (grabbedRigidbody != null)
            {
                grabbedRigidbody.isKinematic = false;
                grabbedRigidbody.useGravity = true;

                // Apply throwing force based on controller velocity
                Vector3 throwVelocity = vrController.GetVelocity() * throwForceMultiplier;
                grabbedRigidbody.velocity = throwVelocity;
            }

            Debug.Log($"Released object: {grabbedObject.name}");

            grabbedObject = null;
            grabbedRigidbody = null;
        }

        private void UpdateGrabbedObject()
        {
            if (grabbedObject == null) return;

            // Smooth follow to grab point
            grabbedObject.transform.position = Vector3.Lerp(
                grabbedObject.transform.position,
                grabPoint.position,
                Time.deltaTime * rotationSpeed
            );

            grabbedObject.transform.rotation = Quaternion.Lerp(
                grabbedObject.transform.rotation,
                grabPoint.rotation,
                Time.deltaTime * rotationSpeed
            );

            previousPosition = grabPoint.position;
            previousRotation = grabPoint.rotation;
        }

        /// <summary>
        /// Check if currently holding an object
        /// </summary>
        public bool IsHoldingObject()
        {
            return grabbedObject != null;
        }

        /// <summary>
        /// Get the currently grabbed object
        /// </summary>
        public GameObject GetGrabbedObject()
        {
            return grabbedObject;
        }

        /// <summary>
        /// Force release the currently held object
        /// </summary>
        public void ForceRelease()
        {
            if (grabbedObject != null)
            {
                ReleaseObject();
            }
        }

        private void OnDrawGizmosSelected()
        {
            if (grabPoint == null) return;

            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(grabPoint.position, grabRadius);
        }
    }
}
