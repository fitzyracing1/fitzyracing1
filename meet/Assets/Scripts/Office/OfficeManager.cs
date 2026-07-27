using UnityEngine;
using Unity.Netcode;
using System.Collections.Generic;

namespace VirtualOffice.Office
{
    /// <summary>
    /// Manages the overall office environment and user sessions
    /// </summary>
    public class OfficeManager : NetworkBehaviour
    {
        public static OfficeManager Instance { get; private set; }

        [Header("Office Settings")]
        [SerializeField] private int maxOccupancy = 20;
        [SerializeField] private GameObject playerPrefab;
        [SerializeField] private Transform[] spawnPoints;

        [Header("Desk Management")]
        [SerializeField] private List<DeskController> availableDesks = new List<DeskController>();

        private Dictionary<ulong, GameObject> activePlayers = new Dictionary<ulong, GameObject>();
        private Dictionary<ulong, DeskController> playerDesks = new Dictionary<ulong, DeskController>();

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }

            FindAllDesks();
        }

        private void Start()
        {
            if (IsServer)
            {
                InitializeOffice();
            }
        }

        private void FindAllDesks()
        {
            DeskController[] desks = FindObjectsOfType<DeskController>();
            availableDesks.AddRange(desks);
            Debug.Log($"Found {availableDesks.Count} desks in office");
        }

        private void InitializeOffice()
        {
            Debug.Log("Office initialized and ready for users");
        }

        /// <summary>
        /// Handle player joining the office
        /// </summary>
        public void OnPlayerJoined(ulong clientId, string playerName)
        {
            if (!IsServer) return;

            Debug.Log($"Player {playerName} (ID: {clientId}) joined the office");

            // Spawn player at available spawn point
            Vector3 spawnPosition = GetAvailableSpawnPoint();
            GameObject player = Instantiate(playerPrefab, spawnPosition, Quaternion.identity);
            
            NetworkObject networkObject = player.GetComponent<NetworkObject>();
            if (networkObject != null)
            {
                networkObject.SpawnAsPlayerObject(clientId);
            }

            activePlayers[clientId] = player;

            // Assign desk to player
            AssignDeskToPlayer(clientId);

            // Notify all clients
            OnPlayerJoinedClientRpc(clientId, playerName);
        }

        /// <summary>
        /// Handle player leaving the office
        /// </summary>
        public void OnPlayerLeft(ulong clientId)
        {
            if (!IsServer) return;

            Debug.Log($"Player (ID: {clientId}) left the office");

            // Free up the desk
            if (playerDesks.ContainsKey(clientId))
            {
                DeskController desk = playerDesks[clientId];
                desk.UnassignUser();
                playerDesks.Remove(clientId);
            }

            // Remove player
            if (activePlayers.ContainsKey(clientId))
            {
                GameObject player = activePlayers[clientId];
                activePlayers.Remove(clientId);
                
                if (player != null)
                {
                    Destroy(player);
                }
            }

            OnPlayerLeftClientRpc(clientId);
        }

        private void AssignDeskToPlayer(ulong clientId)
        {
            foreach (DeskController desk in availableDesks)
            {
                if (!desk.IsOccupied())
                {
                    desk.AssignUser(clientId);
                    playerDesks[clientId] = desk;
                    Debug.Log($"Assigned desk {desk.gameObject.name} to player {clientId}");
                    return;
                }
            }

            Debug.LogWarning($"No available desk for player {clientId}");
        }

        private Vector3 GetAvailableSpawnPoint()
        {
            if (spawnPoints == null || spawnPoints.Length == 0)
            {
                return Vector3.zero;
            }

            int index = activePlayers.Count % spawnPoints.Length;
            return spawnPoints[index].position;
        }

        [ClientRpc]
        private void OnPlayerJoinedClientRpc(ulong clientId, string playerName)
        {
            Debug.Log($"[Client] Player {playerName} joined");
            // Update UI or other client-side effects
        }

        [ClientRpc]
        private void OnPlayerLeftClientRpc(ulong clientId)
        {
            Debug.Log($"[Client] Player left");
            // Update UI or other client-side effects
        }

        /// <summary>
        /// Get the desk assigned to a specific player
        /// </summary>
        public DeskController GetPlayerDesk(ulong clientId)
        {
            if (playerDesks.ContainsKey(clientId))
            {
                return playerDesks[clientId];
            }
            return null;
        }

        /// <summary>
        /// Get the number of players currently in the office
        /// </summary>
        public int GetPlayerCount()
        {
            return activePlayers.Count;
        }

        /// <summary>
        /// Check if the office is at max capacity
        /// </summary>
        public bool IsAtMaxCapacity()
        {
            return activePlayers.Count >= maxOccupancy;
        }

        /// <summary>
        /// Get all active players in the office
        /// </summary>
        public Dictionary<ulong, GameObject> GetActivePlayers()
        {
            return activePlayers;
        }
    }
}
