using UnityEngine;
using Unity.Netcode;
using System.Collections.Generic;
using System.IO;

namespace VirtualOffice.FileSharing
{
    /// <summary>
    /// Manages file sharing operations between users
    /// </summary>
    public class FileManager : NetworkBehaviour
    {
        public static FileManager Instance { get; private set; }

        [Header("File Settings")]
        [SerializeField] private string fileStoragePath = "SharedFiles";
        [SerializeField] private int maxFileSize = 10485760; // 10MB in bytes
        [SerializeField] private string[] allowedExtensions = { ".txt", ".pdf", ".jpg", ".png", ".doc", ".docx" };

        [Header("File Display")]
        [SerializeField] private GameObject fileDisplayPrefab;
        [SerializeField] private Transform fileDisplayContainer;

        private Dictionary<string, SharedFile> sharedFiles = new Dictionary<string, SharedFile>();
        private List<FileDisplay> activeFileDisplays = new List<FileDisplay>();

        [System.Serializable]
        public class SharedFile
        {
            public string fileId;
            public string fileName;
            public string fileExtension;
            public ulong ownerId;
            public string ownerName;
            public byte[] fileData;
            public long fileSize;
            public System.DateTime sharedTime;

            public SharedFile(string id, string name, string extension, ulong owner, string ownerName, byte[] data)
            {
                fileId = id;
                fileName = name;
                fileExtension = extension;
                ownerId = owner;
                this.ownerName = ownerName;
                fileData = data;
                fileSize = data.Length;
                sharedTime = System.DateTime.Now;
            }
        }

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

            InitializeFileStorage();
        }

        private void InitializeFileStorage()
        {
            string fullPath = Path.Combine(Application.persistentDataPath, fileStoragePath);
            
            if (!Directory.Exists(fullPath))
            {
                Directory.CreateDirectory(fullPath);
                Debug.Log($"Created file storage directory: {fullPath}");
            }
        }

        /// <summary>
        /// Share a file with other users
        /// </summary>
        public void ShareFile(string filePath, ulong senderId, string senderName)
        {
            if (!File.Exists(filePath))
            {
                Debug.LogError($"File not found: {filePath}");
                return;
            }

            FileInfo fileInfo = new FileInfo(filePath);

            // Check file size
            if (fileInfo.Length > maxFileSize)
            {
                Debug.LogError($"File too large: {fileInfo.Length} bytes (max: {maxFileSize})");
                return;
            }

            // Check file extension
            if (!IsAllowedExtension(fileInfo.Extension))
            {
                Debug.LogError($"File type not allowed: {fileInfo.Extension}");
                return;
            }

            // Read file data
            byte[] fileData = File.ReadAllBytes(filePath);

            // Create shared file object
            string fileId = System.Guid.NewGuid().ToString();
            SharedFile sharedFile = new SharedFile(
                fileId,
                fileInfo.Name,
                fileInfo.Extension,
                senderId,
                senderName,
                fileData
            );

            // Store file locally
            sharedFiles[fileId] = sharedFile;

            // Notify other users
            if (IsServer)
            {
                BroadcastFileSharedClientRpc(fileId, fileInfo.Name, senderName, fileData.Length);
            }
            else
            {
                ShareFileServerRpc(fileId, fileInfo.Name, fileInfo.Extension, senderId, senderName, fileData);
            }

            Debug.Log($"File shared: {fileInfo.Name} ({fileInfo.Length} bytes)");
        }

        [ServerRpc(RequireOwnership = false)]
        private void ShareFileServerRpc(string fileId, string fileName, string extension, ulong senderId, string senderName, byte[] fileData)
        {
            SharedFile sharedFile = new SharedFile(fileId, fileName, extension, senderId, senderName, fileData);
            sharedFiles[fileId] = sharedFile;

            BroadcastFileSharedClientRpc(fileId, fileName, senderName, fileData.Length);
        }

        [ClientRpc]
        private void BroadcastFileSharedClientRpc(string fileId, string fileName, string senderName, long fileSize)
        {
            Debug.Log($"New file shared: {fileName} by {senderName} ({fileSize} bytes)");
            
            // Update UI or create file display
            CreateFileDisplay(fileId, fileName, senderName, fileSize);
        }

        /// <summary>
        /// Request to download a shared file
        /// </summary>
        public void RequestFile(string fileId, ulong requesterId)
        {
            if (sharedFiles.ContainsKey(fileId))
            {
                SharedFile file = sharedFiles[fileId];
                SendFileDataToClientRpc(requesterId, file.fileId, file.fileName, file.fileData);
            }
            else
            {
                Debug.LogWarning($"File not found: {fileId}");
            }
        }

        [ClientRpc]
        private void SendFileDataToClientRpc(ulong targetClientId, string fileId, string fileName, byte[] fileData)
        {
            // Only process if this is the target client
            if (Unity.Netcode.NetworkManager.Singleton.LocalClientId != targetClientId)
                return;

            // Save file locally
            SaveFileLocally(fileId, fileName, fileData);
        }

        private void SaveFileLocally(string fileId, string fileName, byte[] fileData)
        {
            string fullPath = Path.Combine(Application.persistentDataPath, fileStoragePath, fileName);

            try
            {
                File.WriteAllBytes(fullPath, fileData);
                Debug.Log($"File saved locally: {fullPath}");
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Failed to save file: {ex.Message}");
            }
        }

        private void CreateFileDisplay(string fileId, string fileName, string senderName, long fileSize)
        {
            if (fileDisplayPrefab == null || fileDisplayContainer == null)
                return;

            GameObject displayObj = Instantiate(fileDisplayPrefab, fileDisplayContainer);
            FileDisplay display = displayObj.GetComponent<FileDisplay>();

            if (display != null)
            {
                display.Initialize(fileId, fileName, senderName, fileSize);
                activeFileDisplays.Add(display);
            }
        }

        /// <summary>
        /// Remove a shared file
        /// </summary>
        public void RemoveSharedFile(string fileId)
        {
            if (sharedFiles.ContainsKey(fileId))
            {
                sharedFiles.Remove(fileId);
                Debug.Log($"Removed shared file: {fileId}");

                if (IsServer)
                {
                    RemoveFileClientRpc(fileId);
                }
            }
        }

        [ClientRpc]
        private void RemoveFileClientRpc(string fileId)
        {
            if (sharedFiles.ContainsKey(fileId))
            {
                sharedFiles.Remove(fileId);
            }

            // Remove file display
            FileDisplay display = activeFileDisplays.Find(d => d.GetFileId() == fileId);
            if (display != null)
            {
                activeFileDisplays.Remove(display);
                Destroy(display.gameObject);
            }
        }

        private bool IsAllowedExtension(string extension)
        {
            foreach (string allowed in allowedExtensions)
            {
                if (extension.ToLower() == allowed.ToLower())
                    return true;
            }
            return false;
        }

        /// <summary>
        /// Get all currently shared files
        /// </summary>
        public Dictionary<string, SharedFile> GetSharedFiles()
        {
            return sharedFiles;
        }

        /// <summary>
        /// Get a specific shared file by ID
        /// </summary>
        public SharedFile GetFile(string fileId)
        {
            if (sharedFiles.ContainsKey(fileId))
            {
                return sharedFiles[fileId];
            }
            return null;
        }

        /// <summary>
        /// Clear all shared files
        /// </summary>
        public void ClearAllFiles()
        {
            sharedFiles.Clear();
            
            foreach (FileDisplay display in activeFileDisplays)
            {
                if (display != null)
                {
                    Destroy(display.gameObject);
                }
            }
            
            activeFileDisplays.Clear();
            Debug.Log("All shared files cleared");
        }
    }
}
