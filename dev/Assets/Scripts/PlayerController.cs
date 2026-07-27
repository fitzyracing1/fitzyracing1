using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    public float moveSpeed = 5f;
    public float jumpForce = 10f;

    [Header("Ground Check")]
    public Transform groundCheck;
    public float groundCheckRadius = 0.2f;
    public LayerMask groundLayer;

    private Rigidbody rb;
    private bool isGrounded;
    private float horizontalInput;
    private float verticalInput;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        
        if (groundCheck == null)
        {
            Debug.LogWarning("Ground check not assigned!");
        }
    }

    void Update()
    {
        // Use SimpleInput system
        horizontalInput = SimpleInput.GetHorizontal();
        verticalInput = SimpleInput.GetVertical();

        // Check if grounded
        if (groundCheck != null)
        {
            isGrounded = Physics.CheckSphere(groundCheck.position, groundCheckRadius, groundLayer);
        }

        // Jump
        if (SimpleInput.GetJump() && isGrounded)
        {
            Jump();
        }
    }

    void FixedUpdate()
    {
        // Movement
        Vector3 movement = new Vector3(horizontalInput, 0f, verticalInput) * moveSpeed;
        rb.linearVelocity = new Vector3(movement.x, rb.linearVelocity.y, movement.z);
    }

    void Jump()
    {
        rb.linearVelocity = new Vector3(rb.linearVelocity.x, jumpForce, rb.linearVelocity.z);
    }

    void OnDrawGizmosSelected()
    {
        if (groundCheck != null)
        {
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(groundCheck.position, groundCheckRadius);
        }
    }
}
