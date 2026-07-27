using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace VirtualOffice.FileSharing
{
    /// <summary>
    /// UI display for shared files in the virtual office
    /// </summary>
    public class FileDisplay : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI fileNameText;
        [SerializeField] private TextMeshProUGUI fileSizeText;
        [SerializeField] private TextMeshProUGUI ownerNameText;
        [SerializeField] private Image fileIconImage;
        [SerializeField] private Button downloadButton;
        [SerializeField] private Button viewButton;
        [SerializeField] private Button deleteButton;

        [Header("File Icons")]
        [SerializeField] private Sprite defaultIcon;
        [SerializeField] private Sprite documentIcon;
        [SerializeField] private Sprite imageIcon;
        [SerializeField] private Sprite pdfIcon;

        private string fileId;
        private string fileName;
        private string ownerName;
        private long fileSize;

        private void Start()
        {
            SetupButtons();
        }

        private void SetupButtons()
        {
            if (downloadButton != null)
            {
                downloadButton.onClick.AddListener(OnDownloadClicked);
            }

            if (viewButton != null)
            {
                viewButton.onClick.AddListener(OnViewClicked);
            }

            if (deleteButton != null)
            {
                deleteButton.onClick.AddListener(OnDeleteClicked);
            }
        }

        /// <summary>
        /// Initialize the file display with file information
        /// </summary>
        public void Initialize(string id, string name, string owner, long size)
        {
            fileId = id;
            fileName = name;
            ownerName = owner;
            fileSize = size;

            UpdateDisplay();
        }

        private void UpdateDisplay()
        {
            // Update file name
            if (fileNameText != null)
            {
                fileNameText.text = fileName;
            }

            // Update file size
            if (fileSizeText != null)
            {
                fileSizeText.text = FormatFileSize(fileSize);
            }

            // Update owner name
            if (ownerNameText != null)
            {
                ownerNameText.text = $"Shared by: {ownerName}";
            }

            // Update file icon
            if (fileIconImage != null)
            {
                fileIconImage.sprite = GetFileIcon(fileName);
            }
        }

        private string FormatFileSize(long bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB" };
            double size = bytes;
            int order = 0;

            while (size >= 1024 && order < sizes.Length - 1)
            {
                order++;
                size /= 1024;
            }

            return $"{size:0.##} {sizes[order]}";
        }

        private Sprite GetFileIcon(string fileName)
        {
            string extension = System.IO.Path.GetExtension(fileName).ToLower();

            switch (extension)
            {
                case ".txt":
                case ".doc":
                case ".docx":
                    return documentIcon != null ? documentIcon : defaultIcon;

                case ".jpg":
                case ".jpeg":
                case ".png":
                case ".gif":
                    return imageIcon != null ? imageIcon : defaultIcon;

                case ".pdf":
                    return pdfIcon != null ? pdfIcon : defaultIcon;

                default:
                    return defaultIcon;
            }
        }

        private void OnDownloadClicked()
        {
            Debug.Log($"Download requested for file: {fileName}");

            if (FileManager.Instance != null)
            {
                ulong clientId = Unity.Netcode.NetworkManager.Singleton.LocalClientId;
                FileManager.Instance.RequestFile(fileId, clientId);
            }
        }

        private void OnViewClicked()
        {
            Debug.Log($"View requested for file: {fileName}");

            // Get file from FileManager
            if (FileManager.Instance != null)
            {
                FileManager.SharedFile file = FileManager.Instance.GetFile(fileId);
                
                if (file != null)
                {
                    OpenFileViewer(file);
                }
            }
        }

        private void OnDeleteClicked()
        {
            Debug.Log($"Delete requested for file: {fileName}");

            // Only allow deletion if user is the owner or admin
            if (FileManager.Instance != null)
            {
                FileManager.Instance.RemoveSharedFile(fileId);
            }

            Destroy(gameObject);
        }

        private void OpenFileViewer(FileManager.SharedFile file)
        {
            // Create or open file viewer to display file contents
            // This would typically spawn a 3D canvas or window in VR space
            Debug.Log($"Opening file viewer for: {file.fileName}");

            // For images, you could display them directly
            if (IsImageFile(file.fileExtension))
            {
                DisplayImage(file.fileData);
            }
            // For text files, display the content
            else if (IsTextFile(file.fileExtension))
            {
                DisplayText(file.fileData);
            }
            // For other files, show file info
            else
            {
                Debug.Log($"File type {file.fileExtension} requires external viewer");
            }
        }

        private bool IsImageFile(string extension)
        {
            string[] imageExtensions = { ".jpg", ".jpeg", ".png", ".gif", ".bmp" };
            foreach (string ext in imageExtensions)
            {
                if (extension.ToLower() == ext)
                    return true;
            }
            return false;
        }

        private bool IsTextFile(string extension)
        {
            string[] textExtensions = { ".txt", ".json", ".xml", ".csv" };
            foreach (string ext in textExtensions)
            {
                if (extension.ToLower() == ext)
                    return true;
            }
            return false;
        }

        private void DisplayImage(byte[] imageData)
        {
            // Create texture from image data
            Texture2D texture = new Texture2D(2, 2);
            if (texture.LoadImage(imageData))
            {
                Debug.Log("Image loaded successfully");
                // Display texture on a 3D plane or UI canvas in VR
            }
        }

        private void DisplayText(byte[] textData)
        {
            string content = System.Text.Encoding.UTF8.GetString(textData);
            Debug.Log($"Text content: {content.Substring(0, Mathf.Min(100, content.Length))}...");
            // Display text in a 3D text panel in VR
        }

        /// <summary>
        /// Get the file ID associated with this display
        /// </summary>
        public string GetFileId()
        {
            return fileId;
        }

        /// <summary>
        /// Get the file name
        /// </summary>
        public string GetFileName()
        {
            return fileName;
        }

        private void OnDestroy()
        {
            if (downloadButton != null)
            {
                downloadButton.onClick.RemoveListener(OnDownloadClicked);
            }

            if (viewButton != null)
            {
                viewButton.onClick.RemoveListener(OnViewClicked);
            }

            if (deleteButton != null)
            {
                deleteButton.onClick.RemoveListener(OnDeleteClicked);
            }
        }
    }
}
