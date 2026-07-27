namespace AspectControlUnit.Models;

/// <summary>
/// Represents an inventory item containing data
/// </summary>
public class InventoryItem
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public double Value { get; set; }
    public string Category { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
