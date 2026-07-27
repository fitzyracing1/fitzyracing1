namespace AspectControlUnit.Models;

/// <summary>
/// Represents a dataset for processing
/// </summary>
public class DataSet
{
    public string Id { get; set; } = string.Empty;
    public List<double> Values { get; set; } = new();
    public string Source { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}
