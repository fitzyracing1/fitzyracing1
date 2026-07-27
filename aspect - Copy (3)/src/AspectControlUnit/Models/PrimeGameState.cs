namespace AspectControlUnit.Models;

/// <summary>
/// Represents game state for prime number game
/// </summary>
public class PrimeGameState
{
    public int CurrentNumber { get; set; }
    public bool IsPrime { get; set; }
    public int Score { get; set; }
    public List<int> PrimesFound { get; set; } = new();
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}
