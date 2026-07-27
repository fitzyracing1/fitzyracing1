using UnityEngine;
using Unity.Netcode;

namespace VirtualOffice.Networking
{
    /// <summary>
    /// Manages individual player network state and synchronization
    /// </summary>
    public class PlayerNetwork : NetworkBehaviour
    {
        [Header("Player Info")]
        [SerializeField] private string playerName = "Player";
        
        private NetworkVariable<Vector3> networkPosition = new NetworkVariable<Vector3>();
        private NetworkVariable<Quaternion> networkRotation = new NetworkVariable<Quaternion>();
        private NetworkVariable<FixedString64Bytes> networkPlayerName = new NetworkVariable<FixedString64Bytes>();

        [Header("Sync Settings")]
        [SerializeField] private float positionLerpSpeed = 10f;
        [SerializeField] private float rotationLerpSpeed = 10f;

        private Transform playerTransform;

        private void Awake()
        {
            playerTransform = transform;
        }

        public override void OnNetworkSpawn()
        {
            base.OnNetworkSpawn();

            if (IsOwner)
            {
                // Set initial player name
                SetPlayerNameServerRpc(playerName);
            }
            else
            {
                // For remote players, subscribe to position changes
                networkPosition.OnValueChanged += OnPositionChanged;
                networkRotation.OnValueChanged += OnRotationChanged;
            }

            Debug.Log($"Player spawned: {networkPlayerName.Value}");
        }

        private void Update()
        {
            if (IsOwner)
            {
                // Update network position and rotation for this player
                UpdatePositionServerRpc(playerTransform.position);
                UpdateRotationServerRpc(playerTransform.rotation);
            }
            else
            {
                // Interpolate remote player position and rotation
                playerTransform.position = Vector3.Lerp(
                    playerTransform.position,
                    networkPosition.Value,
                    Time.deltaTime * positionLerpSpeed
                );

                playerTransform.rotation = Quaternion.Lerp(
                    playerTransform.rotation,
                    networkRotation.Value,
                    Time.deltaTime * rotationLerpSpeed
                );
            }
        }

        [ServerRpc]
        private void UpdatePositionServerRpc(Vector3 position)
        {
            networkPosition.Value = position;
        }

        [ServerRpc]
        private void UpdateRotationServerRpc(Quaternion rotation)
        {
            networkRotation.Value = rotation;
        }

        [ServerRpc]
        private void SetPlayerNameServerRpc(string name)
        {
            networkPlayerName.Value = name;
        }

        private void OnPositionChanged(Vector3 oldValue, Vector3 newValue)
        {
            // Position changed callback for remote players
        }

        private void OnRotationChanged(Quaternion oldValue, Quaternion newValue)
        {
            // Rotation changed callback for remote players
        }

        /// <summary>
        /// Set the player's display name
        /// </summary>
        public void SetPlayerName(string name)
        {
            playerName = name;
            if (IsOwner)
            {
                SetPlayerNameServerRpc(name);
            }
        }

        /// <summary>
        /// Get the player's display name
        /// </summary>
        public string GetPlayerName()
        {
            return networkPlayerName.Value.ToString();
        }

        public override void OnNetworkDespawn()
        {
            base.OnNetworkDespawn();

            if (!IsOwner)
            {
                networkPosition.OnValueChanged -= OnPositionChanged;
                networkRotation.OnValueChanged -= OnRotationChanged;
            }
        }
    }
}
