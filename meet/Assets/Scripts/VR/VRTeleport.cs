using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

namespace VirtualOffice.VR
{
    /// <summary>
    /// Handles VR teleportation for movement in the virtual office
    /// </summary>
    public class VRTeleport : MonoBehaviour
    {
        [Header("Teleport Settings")]
        [SerializeField] private VRController vrController;
        [SerializeField] private Transform playerRig;
        [SerializeField] private LayerMask teleportLayer;
        [SerializeField] private float maxTeleportDistance = 10f;

        [Header("Visual Feedback")]
        [SerializeField] private LineRenderer teleportLine;
        [SerializeField] private GameObject teleportMarker;
        [SerializeField] private Color validTeleportColor = Color.green;
        [SerializeField] private Color invalidTeleportColor = Color.red;

        [Header("Arc Settings")]
        [SerializeField] private float arcHeight = 2f;
        [SerializeField] private int arcSegments = 20;
        [SerializeField] private float arcDuration = 1f;

        private bool isTeleportActive;
        private Vector3 teleportDestination;
        private bool isValidTeleport;

        private void Awake()
        {
            if (vrController == null)
            {
                vrController = GetComponent<VRController>();
            }

            if (teleportLine == null)
            {
                teleportLine = gameObject.AddComponent<LineRenderer>();
                ConfigureTeleportLine();
            }

            if (teleportMarker != null)
            {
                teleportMarker.SetActive(false);
            }
        }

        private void Update()
        {
            if (vrController == null) return;

            if (vrController.IsTriggerPressed())
            {
                ShowTeleportArc();
                isTeleportActive = true;
            }
            else if (isTeleportActive)
            {
                ExecuteTeleport();
                isTeleportActive = false;
            }

            if (!isTeleportActive)
            {
                HideTeleportArc();
            }
        }

        private void ShowTeleportArc()
        {
            RaycastHit hit;
            Vector3 startPoint = transform.position;
            Vector3 forward = transform.forward;

            // Calculate arc points
            Vector3[] arcPoints = CalculateArcPoints(startPoint, forward);

            // Check if teleport destination is valid
            isValidTeleport = false;

            for (int i = 0; i < arcPoints.Length - 1; i++)
            {
                Vector3 direction = arcPoints[i + 1] - arcPoints[i];
                float distance = direction.magnitude;

                if (Physics.Raycast(arcPoints[i], direction.normalized, out hit, distance, teleportLayer))
                {
                    teleportDestination = hit.point;
                    isValidTeleport = true;

                    // Update line renderer to stop at hit point
                    UpdateTeleportLine(arcPoints, i + 1);
                    UpdateTeleportMarker(hit.point, true);
                    return;
                }
            }

            // No valid hit found
            UpdateTeleportLine(arcPoints, arcPoints.Length);
            UpdateTeleportMarker(arcPoints[arcPoints.Length - 1], false);
        }

        private Vector3[] CalculateArcPoints(Vector3 startPoint, Vector3 forward)
        {
            Vector3[] points = new Vector3[arcSegments];
            
            for (int i = 0; i < arcSegments; i++)
            {
                float t = i / (float)(arcSegments - 1);
                float horizontalDistance = maxTeleportDistance * t;
                float verticalOffset = arcHeight * Mathf.Sin(t * Mathf.PI);

                Vector3 point = startPoint + forward * horizontalDistance;
                point.y += verticalOffset - (arcHeight * t * t); // Gravity effect

                points[i] = point;
            }

            return points;
        }

        private void UpdateTeleportLine(Vector3[] points, int pointCount)
        {
            if (teleportLine == null) return;

            teleportLine.positionCount = pointCount;
            for (int i = 0; i < pointCount; i++)
            {
                teleportLine.SetPosition(i, points[i]);
            }

            teleportLine.startColor = isValidTeleport ? validTeleportColor : invalidTeleportColor;
            teleportLine.endColor = isValidTeleport ? validTeleportColor : invalidTeleportColor;
            teleportLine.enabled = true;
        }

        private void UpdateTeleportMarker(Vector3 position, bool valid)
        {
            if (teleportMarker == null) return;

            teleportMarker.SetActive(true);
            teleportMarker.transform.position = position;

            Renderer markerRenderer = teleportMarker.GetComponent<Renderer>();
            if (markerRenderer != null)
            {
                markerRenderer.material.color = valid ? validTeleportColor : invalidTeleportColor;
            }
        }

        private void HideTeleportArc()
        {
            if (teleportLine != null)
            {
                teleportLine.enabled = false;
            }

            if (teleportMarker != null)
            {
                teleportMarker.SetActive(false);
            }
        }

        private void ExecuteTeleport()
        {
            if (!isValidTeleport || playerRig == null) return;

            // Teleport player to destination
            Vector3 offset = teleportDestination - transform.position;
            offset.y = 0; // Keep vertical position
            playerRig.position += offset;

            Debug.Log($"Teleported to: {teleportDestination}");
        }

        private void ConfigureTeleportLine()
        {
            teleportLine.startWidth = 0.02f;
            teleportLine.endWidth = 0.02f;
            teleportLine.material = new Material(Shader.Find("Sprites/Default"));
            teleportLine.enabled = false;
        }

        /// <summary>
        /// Check if teleport is currently active
        /// </summary>
        public bool IsTeleportActive()
        {
            return isTeleportActive;
        }

        /// <summary>
        /// Set the maximum teleport distance
        /// </summary>
        public void SetMaxDistance(float distance)
        {
            maxTeleportDistance = Mathf.Max(1f, distance);
        }
    }
}
