namespace AspectControlUnit.Models;

/// <summary>
/// Represents a computed difference between two values
/// </summary>
public class ComputeDifference
{
    public object? ValueA { get; set; }
    public object? ValueB { get; set; }
    public object? Difference { get; set; }
    public string DifferenceType { get; set; } = string.Empty;
    public DateTime ComputedAt { get; set; } = DateTime.UtcNow;
}
