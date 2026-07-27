using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [Header("Target Settings")]
    public Transform target;

    [Header("Camera Settings")]
    public Vector3 offset = new Vector3(0f, 5f, -10f);
    public float smoothSpeed = 0.125f;
    public bool lookAtTarget = true;

    void LateUpdate()
    {
        if (target == null)
        {
            Debug.LogWarning("Camera target not assigned!");
            return;
        }

        // Calculate desired position
        Vector3 desiredPosition = target.position + offset;

        // Smoothly move the camera
        Vector3 smoothedPosition = Vector3.Lerp(transform.position, desiredPosition, smoothSpeed);
        transform.position = smoothedPosition;

        // Look at the target
        if (lookAtTarget)
        {
            transform.LookAt(target);
        }
    }
}
