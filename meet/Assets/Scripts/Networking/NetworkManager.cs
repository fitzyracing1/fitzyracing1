using UnityEngine;
using Unity.Netcode;

namespace VirtualOffice.Networking
{
    /// <summary>
    /// Manages network connections and multiplayer sessions
    /// </summary>
    public class NetworkManager : MonoBehaviour
    {
        public static NetworkManager Instance { get; private set; }

        [Header("Network Settings")]
        [SerializeField] private string serverAddress = "127.0.0.1";
        [SerializeField] private ushort serverPort = 7777;
        [SerializeField] private int maxPlayers = 10;

        private Unity.Netcode.NetworkManager networkManager;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            networkManager = GetComponent<Unity.Netcode.NetworkManager>();
            
            if (networkManager == null)
            {
                networkManager = gameObject.AddComponent<Unity.Netcode.NetworkManager>();
            }
        }

        /// <summary>
        /// Start the network as a host (server + client)
        /// </summary>
        public void StartHost()
        {
            if (networkManager != null)
            {
                networkManager.StartHost();
                Debug.Log("Started as Host");
            }
        }

        /// <summary>
        /// Start the network as a server only
        /// </summary>
        public void StartServer()
        {
            if (networkManager != null)
            {
                networkManager.StartServer();
                Debug.Log("Started as Server");
            }
        }

        /// <summary>
        /// Connect to a server as a client
        /// </summary>
        public void StartClient()
        {
            if (networkManager != null)
            {
                networkManager.StartClient();
                Debug.Log("Started as Client");
            }
        }

        /// <summary>
        /// Disconnect from the network
        /// </summary>
        public void Disconnect()
        {
            if (networkManager != null)
            {
                networkManager.Shutdown();
                Debug.Log("Disconnected from network");
            }
        }

        /// <summary>
        /// Get the current number of connected players
        /// </summary>
        public int GetConnectedPlayerCount()
        {
            if (networkManager != null && networkManager.IsServer)
            {
                return (int)networkManager.ConnectedClients.Count;
            }
            return 0;
        }

        /// <summary>
        /// Check if this instance is the server
        /// </summary>
        public bool IsServer()
        {
            return networkManager != null && networkManager.IsServer;
        }

        /// <summary>
        /// Check if this instance is a client
        /// </summary>
        public bool IsClient()
        {
            return networkManager != null && networkManager.IsClient;
        }

        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }
    }
}
