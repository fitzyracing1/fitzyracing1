using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace VirtualOffice.Office
{
    /// <summary>
    /// Handles user login and authentication for the virtual office
    /// </summary>
    public class UserLogin : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private GameObject loginPanel;
        [SerializeField] private TMP_InputField usernameInput;
        [SerializeField] private Button loginButton;
        [SerializeField] private TextMeshProUGUI statusText;

        [Header("Settings")]
        [SerializeField] private int minUsernameLength = 3;
        [SerializeField] private int maxUsernameLength = 20;

        private string currentUsername;
        private bool isLoggedIn = false;

        private void Start()
        {
            SetupLoginUI();
        }

        private void SetupLoginUI()
        {
            if (loginButton != null)
            {
                loginButton.onClick.AddListener(OnLoginButtonClicked);
            }

            if (usernameInput != null)
            {
                usernameInput.onValueChanged.AddListener(OnUsernameChanged);
            }

            ShowLoginPanel();
        }

        private void OnUsernameChanged(string username)
        {
            // Enable/disable login button based on username validity
            if (loginButton != null)
            {
                loginButton.interactable = IsValidUsername(username);
            }
        }

        private void OnLoginButtonClicked()
        {
            string username = usernameInput != null ? usernameInput.text : "";

            if (IsValidUsername(username))
            {
                AttemptLogin(username);
            }
            else
            {
                ShowStatus("Invalid username. Please try again.", false);
            }
        }

        private bool IsValidUsername(string username)
        {
            if (string.IsNullOrWhiteSpace(username))
                return false;

            if (username.Length < minUsernameLength || username.Length > maxUsernameLength)
                return false;

            // Check for valid characters (alphanumeric and underscore)
            foreach (char c in username)
            {
                if (!char.IsLetterOrDigit(c) && c != '_')
                    return false;
            }

            return true;
        }

        private void AttemptLogin(string username)
        {
            ShowStatus("Logging in...", true);

            // Store username
            currentUsername = username;

            // In a real application, you would authenticate with a server here
            // For now, we'll just simulate a successful login
            StartCoroutine(SimulateLogin());
        }

        private System.Collections.IEnumerator SimulateLogin()
        {
            yield return new WaitForSeconds(1f);

            // Successful login
            isLoggedIn = true;
            ShowStatus($"Welcome, {currentUsername}!", true);

            yield return new WaitForSeconds(1f);

            // Hide login panel and start session
            HideLoginPanel();
            StartOfficeSession();
        }

        private void StartOfficeSession()
        {
            Debug.Log($"Starting office session for user: {currentUsername}");

            // Initialize network connection
            if (Networking.NetworkManager.Instance != null)
            {
                // Try to connect as client or start as host
                // This would be customized based on your networking setup
                Networking.NetworkManager.Instance.StartHost();
            }

            // Notify OfficeManager of new player
            if (OfficeManager.Instance != null)
            {
                // The actual player spawn will be handled by the network manager
                Debug.Log("Office session started");
            }
        }

        private void ShowLoginPanel()
        {
            if (loginPanel != null)
            {
                loginPanel.SetActive(true);
            }
        }

        private void HideLoginPanel()
        {
            if (loginPanel != null)
            {
                loginPanel.SetActive(false);
            }
        }

        private void ShowStatus(string message, bool isSuccess)
        {
            if (statusText != null)
            {
                statusText.text = message;
                statusText.color = isSuccess ? Color.green : Color.red;
            }

            Debug.Log($"Login Status: {message}");
        }

        /// <summary>
        /// Get the current logged-in username
        /// </summary>
        public string GetUsername()
        {
            return currentUsername;
        }

        /// <summary>
        /// Check if user is currently logged in
        /// </summary>
        public bool IsLoggedIn()
        {
            return isLoggedIn;
        }

        /// <summary>
        /// Log out the current user
        /// </summary>
        public void Logout()
        {
            if (!isLoggedIn) return;

            Debug.Log($"User {currentUsername} logged out");

            // Disconnect from network
            if (Networking.NetworkManager.Instance != null)
            {
                Networking.NetworkManager.Instance.Disconnect();
            }

            // Reset state
            isLoggedIn = false;
            currentUsername = "";

            // Show login panel again
            ShowLoginPanel();
        }

        private void OnDestroy()
        {
            if (loginButton != null)
            {
                loginButton.onClick.RemoveListener(OnLoginButtonClicked);
            }

            if (usernameInput != null)
            {
                usernameInput.onValueChanged.RemoveListener(OnUsernameChanged);
            }
        }
    }
}
