using UnityEngine;

namespace VirtualOffice
{
    /// <summary>
    /// Example script showing how to use the Virtual Office system
    /// </summary>
    public class ExampleUsage : MonoBehaviour
    {
        private void Start()
        {
            // Example 1: Start hosting a virtual office
            StartHost();

            // Example 2: Join an existing office
            // JoinOffice();

            // Example 3: Share a file
            // ShareExampleFile();
        }

        /// <summary>
        /// Example: Start as host
        /// </summary>
        private void StartHost()
        {
            if (Networking.NetworkManager.Instance != null)
            {
                Networking.NetworkManager.Instance.StartHost();
                Debug.Log("Started virtual office as host");
            }
        }

        /// <summary>
        /// Example: Join as client
        /// </summary>
        private void JoinOffice()
        {
            if (Networking.NetworkManager.Instance != null)
            {
                Networking.NetworkManager.Instance.StartClient();
                Debug.Log("Joining virtual office as client");
            }
        }

        /// <summary>
        /// Example: Share a file with other users
        /// </summary>
        private void ShareExampleFile()
        {
            // Path to the file you want to share
            string filePath = "C:\\Users\\Documents\\example.txt";

            // Get current user info
            ulong userId = Unity.Netcode.NetworkManager.Singleton.LocalClientId;
            string userName = "ExampleUser";

            // Share the file
            if (FileSharing.FileManager.Instance != null)
            {
                FileSharing.FileManager.Instance.ShareFile(filePath, userId, userName);
                Debug.Log($"Shared file: {filePath}");
            }
        }

        /// <summary>
        /// Example: Get assigned desk
        /// </summary>
        private void GetMyDesk()
        {
            ulong myClientId = Unity.Netcode.NetworkManager.Singleton.LocalClientId;

            if (Office.OfficeManager.Instance != null)
            {
                Office.DeskController myDesk = Office.OfficeManager.Instance.GetPlayerDesk(myClientId);
                
                if (myDesk != null)
                {
                    Debug.Log($"My desk ID: {myDesk.GetDeskId()}");
                    Debug.Log($"Desk position: {myDesk.GetSeatPosition()}");
                }
            }
        }

        /// <summary>
        /// Example: Teleport to desk
        /// </summary>
        private void TeleportToMyDesk()
        {
            ulong myClientId = Unity.Netcode.NetworkManager.Singleton.LocalClientId;

            if (Office.OfficeManager.Instance != null)
            {
                Office.DeskController myDesk = Office.OfficeManager.Instance.GetPlayerDesk(myClientId);
                
                if (myDesk != null)
                {
                    // Assuming you have a reference to the player's transform
                    Transform playerTransform = transform;
                    myDesk.TeleportPlayerToDesk(playerTransform);
                    Debug.Log("Teleported to desk");
                }
            }
        }

        /// <summary>
        /// Example: Check VR controller input
        /// </summary>
        private void Update()
        {
            // This would typically be in a controller-specific script
            // Just showing the API usage here

            // Check if using VR controllers
            VR.VRController leftController = GameObject.Find("LeftController")?.GetComponent<VR.VRController>();
            
            if (leftController != null)
            {
                if (leftController.IsTriggerPressed())
                {
                    Debug.Log("Left trigger pressed");
                }

                if (leftController.IsGripPressed())
                {
                    Debug.Log("Left grip pressed");
                }

                Vector3 velocity = leftController.GetVelocity();
                if (velocity.magnitude > 1f)
                {
                    Debug.Log($"Controller moving at {velocity.magnitude} m/s");
                }
            }
        }

        /// <summary>
        /// Example: Download a shared file
        /// </summary>
        private void DownloadFile(string fileId)
        {
            ulong myClientId = Unity.Netcode.NetworkManager.Singleton.LocalClientId;

            if (FileSharing.FileManager.Instance != null)
            {
                FileSharing.FileManager.Instance.RequestFile(fileId, myClientId);
                Debug.Log($"Requesting file: {fileId}");
            }
        }

        /// <summary>
        /// Example: List all shared files
        /// </summary>
        private void ListSharedFiles()
        {
            if (FileSharing.FileManager.Instance != null)
            {
                var files = FileSharing.FileManager.Instance.GetSharedFiles();

                Debug.Log($"Total shared files: {files.Count}");

                foreach (var file in files.Values)
                {
                    Debug.Log($"- {file.fileName} ({file.fileSize} bytes) by {file.ownerName}");
                }
            }
        }

        /// <summary>
        /// Example: Get number of users in office
        /// </summary>
        private void GetUserCount()
        {
            if (Office.OfficeManager.Instance != null)
            {
                int playerCount = Office.OfficeManager.Instance.GetPlayerCount();
                bool isAtCapacity = Office.OfficeManager.Instance.IsAtMaxCapacity();

                Debug.Log($"Players in office: {playerCount}");
                Debug.Log($"At max capacity: {isAtCapacity}");
            }
        }
    }
}
