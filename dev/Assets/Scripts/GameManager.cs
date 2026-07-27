using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [Header("Game Settings")]
    public int maxLives = 3;
    public int score = 0;

    private int currentLives;

    void Awake()
    {
        // Singleton pattern
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

    void Start()
    {
        currentLives = maxLives;
    }

    public void AddScore(int points)
    {
        score += points;
        Debug.Log($"Score: {score}");
    }

    public void LoseLife()
    {
        currentLives--;
        Debug.Log($"Lives remaining: {currentLives}");

        if (currentLives <= 0)
        {
            GameOver();
        }
    }

    public void RestartGame()
    {
        score = 0;
        currentLives = maxLives;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }

    void GameOver()
    {
        Debug.Log("Game Over!");
        // Add game over logic here
    }
}
