using UnityEngine;
using Unity.Netcode;

namespace VirtualOffice.Office
{
    /// <summary>
    /// Controls individual desk functionality and user assignment
    /// </summary>
    public class DeskController : NetworkBehaviour
    {
        [Header("Desk Info")]
        [SerializeField] private string deskId;
        [SerializeField] private Transform seatPosition;
        
        [Header("Visual Settings")]
        [SerializeField] private GameObject deskModel;
        [SerializeField] private Material occupiedMaterial;
        [SerializeField] private Material availableMaterial;
        [SerializeField] private Renderer deskRenderer;

        [Header("Desk Items")]
        [SerializeField] private Transform monitorPosition;
        [SerializeField] private Transform keyboardPosition;
        [SerializeField] private Transform documentHolderPosition;

        private NetworkVariable<bool> isOccupied = new NetworkVariable<bool>(false);
        private NetworkVariable<ulong> assignedUserId = new NetworkVariable<ulong>(0);
        private NetworkVariable<FixedString64Bytes> assignedUserName = new NetworkVariable<FixedString64Bytes>("");

        private void Awake()
        {
            if (string.IsNullOrEmpty(deskId))
            {
                deskId = System.Guid.NewGuid().ToString();
            }

            if (deskRenderer == null && deskModel != null)
            {
                deskRenderer = deskModel.GetComponent<Renderer>();
            }
        }

        public override void OnNetworkSpawn()
        {
            base.OnNetworkSpawn();
            
            isOccupied.OnValueChanged += OnOccupiedStateChanged;
            UpdateDeskVisuals();
        }

        /// <summary>
        /// Assign a user to this desk
        /// </summary>
        public void AssignUser(ulong userId, string userName = "")
        {
            if (!IsServer) return;

            if (isOccupied.Value)
            {
                Debug.LogWarning($"Desk {deskId} is already occupied");
                return;
            }

            isOccupied.Value = true;
            assignedUserId.Value = userId;
            assignedUserName.Value = userName;

            Debug.Log($"Desk {deskId} assigned to user {userId}");
        }

        /// <summary>
        /// Remove user assignment from this desk
        /// </summary>
        public void UnassignUser()
        {
            if (!IsServer) return;

            isOccupied.Value = false;
            assignedUserId.Value = 0;
            assignedUserName.Value = "";

            Debug.Log($"Desk {deskId} is now available");
        }

        /// <summary>
        /// Check if this desk is currently occupied
        /// </summary>
        public bool IsOccupied()
        {
            return isOccupied.Value;
        }

        /// <summary>
        /// Get the ID of the user assigned to this desk
        /// </summary>
        public ulong GetAssignedUserId()
        {
            return assignedUserId.Value;
        }

        /// <summary>
        /// Get the name of the user assigned to this desk
        /// </summary>
        public string GetAssignedUserName()
        {
            return assignedUserName.Value.ToString();
        }

        /// <summary>
        /// Get the seat position for this desk
        /// </summary>
        public Vector3 GetSeatPosition()
        {
            return seatPosition != null ? seatPosition.position : transform.position;
        }

        /// <summary>
        /// Get the desk's unique identifier
        /// </summary>
        public string GetDeskId()
        {
            return deskId;
        }

        private void OnOccupiedStateChanged(bool oldValue, bool newValue)
        {
            UpdateDeskVisuals();
        }

        private void UpdateDeskVisuals()
        {
            if (deskRenderer == null) return;

            deskRenderer.material = isOccupied.Value ? occupiedMaterial : availableMaterial;
        }

        /// <summary>
        /// Place an item on the desk at a specific position
        /// </summary>
        public void PlaceItem(GameObject item, string itemType)
        {
            Transform targetPosition = null;

            switch (itemType.ToLower())
            {
                case "monitor":
                    targetPosition = monitorPosition;
                    break;
                case "keyboard":
                    targetPosition = keyboardPosition;
                    break;
                case "document":
                    targetPosition = documentHolderPosition;
                    break;
                default:
                    targetPosition = transform;
                    break;
            }

            if (targetPosition != null && item != null)
            {
                item.transform.position = targetPosition.position;
                item.transform.rotation = targetPosition.rotation;
                item.transform.SetParent(targetPosition);
            }
        }

        /// <summary>
        /// Teleport player to desk seat position
        /// </summary>
        public void TeleportPlayerToDesk(Transform playerTransform)
        {
            if (playerTransform != null && seatPosition != null)
            {
                playerTransform.position = seatPosition.position;
                playerTransform.rotation = seatPosition.rotation;
            }
        }

        public override void OnNetworkDespawn()
        {
            base.OnNetworkDespawn();
            isOccupied.OnValueChanged -= OnOccupiedStateChanged;
        }

        private void OnDrawGizmosSelected()
        {
            if (seatPosition != null)
            {
                Gizmos.color = Color.blue;
                Gizmos.DrawWireSphere(seatPosition.position, 0.3f);
                Gizmos.DrawLine(seatPosition.position, seatPosition.position + seatPosition.forward * 0.5f);
            }
        }
    }
}
