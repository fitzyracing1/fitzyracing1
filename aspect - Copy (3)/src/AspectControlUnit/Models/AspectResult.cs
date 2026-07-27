namespace AspectControlUnit.Interfaces;

/// <summary>
/// Result of an aspect execution
/// </summary>
public class AspectResult
{
    public string AspectId { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public object? Data { get; set; }
    public DateTime ExecutedAt { get; set; } = DateTime.UtcNow;
}
