using UnityEngine;
using Unity.Netcode;

namespace VirtualOffice.FileSharing
{
    /// <summary>
    /// Handles real-time file synchronization between clients
    /// </summary>
    public class FileSync : NetworkBehaviour
    {
        public static FileSync Instance { get; private set; }

        [Header("Sync Settings")]
        [SerializeField] private float syncInterval = 2f;
        [SerializeField] private bool autoSync = true;

        private float syncTimer;

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
        }

        private void Update()
        {
            if (!autoSync || !IsServer) return;

            syncTimer += Time.deltaTime;

            if (syncTimer >= syncInterval)
            {
                SyncFiles();
                syncTimer = 0f;
            }
        }

        /// <summary>
        /// Synchronize file list across all clients
        /// </summary>
        public void SyncFiles()
        {
            if (!IsServer) return;

            if (FileManager.Instance == null) return;

            var sharedFiles = FileManager.Instance.GetSharedFiles();

            foreach (var file in sharedFiles.Values)
            {
                SyncFileMetadataClientRpc(
                    file.fileId,
                    file.fileName,
                    file.fileExtension,
                    file.ownerId,
                    file.ownerName,
                    file.fileSize
                );
            }
        }

        [ClientRpc]
        private void SyncFileMetadataClientRpc(
            string fileId,
            string fileName,
            string extension,
            ulong ownerId,
            string ownerName,
            long fileSize)
        {
            if (IsServer) return; // Server already has this data

            // Update local file registry with metadata
            Debug.Log($"[Sync] File metadata received: {fileName}");
        }

        /// <summary>
        /// Request full file sync from server
        /// </summary>
        public void RequestFullSync()
        {
            if (IsServer)
            {
                SyncFiles();
            }
            else
            {
                RequestFullSyncServerRpc();
            }
        }

        [ServerRpc(RequireOwnership = false)]
        private void RequestFullSyncServerRpc(ServerRpcParams rpcParams = default)
        {
            ulong clientId = rpcParams.Receive.SenderClientId;
            Debug.Log($"Full sync requested by client {clientId}");

            // Send all files to requesting client
            if (FileManager.Instance != null)
            {
                var sharedFiles = FileManager.Instance.GetSharedFiles();

                foreach (var file in sharedFiles.Values)
                {
                    SendFileToClientRpc(
                        clientId,
                        file.fileId,
                        file.fileName,
                        file.fileExtension,
                        file.ownerId,
                        file.ownerName,
                        file.fileData
                    );
                }
            }
        }

        [ClientRpc]
        private void SendFileToClientRpc(
            ulong targetClientId,
            string fileId,
            string fileName,
            string extension,
            ulong ownerId,
            string ownerName,
            byte[] fileData)
        {
            // Only process if this is the target client
            if (Unity.Netcode.NetworkManager.Singleton.LocalClientId != targetClientId)
                return;

            Debug.Log($"[Sync] Received file: {fileName}");

            // Add file to local FileManager
            // This would typically recreate the SharedFile object locally
        }

        /// <summary>
        /// Notify all clients of a new file being shared
        /// </summary>
        public void BroadcastNewFile(string fileId, string fileName, string ownerName)
        {
            if (!IsServer) return;

            NotifyNewFileClientRpc(fileId, fileName, ownerName);
        }

        [ClientRpc]
        private void NotifyNewFileClientRpc(string fileId, string fileName, string ownerName)
        {
            Debug.Log($"[Sync] New file available: {fileName} shared by {ownerName}");
            
            // Trigger UI notification or update
            ShowFileNotification(fileName, ownerName);
        }

        /// <summary>
        /// Notify all clients of a file being removed
        /// </summary>
        public void BroadcastFileRemoval(string fileId)
        {
            if (!IsServer) return;

            NotifyFileRemovedClientRpc(fileId);
        }

        [ClientRpc]
        private void NotifyFileRemovedClientRpc(string fileId)
        {
            Debug.Log($"[Sync] File removed: {fileId}");

            // Update local file list
            if (FileManager.Instance != null)
            {
                FileManager.Instance.RemoveSharedFile(fileId);
            }
        }

        private void ShowFileNotification(string fileName, string ownerName)
        {
            // Display a notification in VR space
            // This could be a floating text or UI element
            Debug.Log($"Notification: {ownerName} shared {fileName}");
        }

        /// <summary>
        /// Set the sync interval
        /// </summary>
        public void SetSyncInterval(float interval)
        {
            syncInterval = Mathf.Max(0.5f, interval);
        }

        /// <summary>
        /// Enable or disable auto sync
        /// </summary>
        public void SetAutoSync(bool enabled)
        {
            autoSync = enabled;
        }

        /// <summary>
        /// Force immediate sync
        /// </summary>
        public void ForceSyncNow()
        {
            if (IsServer)
            {
                SyncFiles();
            }
            else
            {
                RequestFullSync();
            }
        }

        public override void OnNetworkSpawn()
        {
            base.OnNetworkSpawn();

            // Request initial sync when joining
            if (!IsServer)
            {
                Invoke(nameof(RequestFullSync), 1f);
            }
        }
    }
}
