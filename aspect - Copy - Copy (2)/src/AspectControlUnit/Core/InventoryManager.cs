using AspectControlUnit.Models;

namespace AspectControlUnit.Core;

/// <summary>
/// Manages inventory data for processing
/// </summary>
public class InventoryManager
{
    private readonly List<InventoryItem> _inventory = new();
    private readonly Dictionary<string, DataSet> _dataSets = new();

    public void AddItem(InventoryItem item)
    {
        _inventory.Add(item);
    }

    public DataSet CreateDataSetFromInventory(string category)
    {
        var items = _inventory.Where(i => i.Category == category).ToList();
        var dataSet = new DataSet
        {
            Id = Guid.NewGuid().ToString(),
            Source = $"Inventory-{category}",
            Values = items.Select(i => i.Value).ToList(),
            Timestamp = DateTime.UtcNow
        };

        _dataSets[dataSet.Id] = dataSet;
        return dataSet;
    }

    public DataSet? GetDataSet(string id)
    {
        return _dataSets.TryGetValue(id, out var dataSet) ? dataSet : null;
    }

    public List<InventoryItem> GetInventory() => _inventory;

    public int GetInventoryCount() => _inventory.Count;

    public void ClearInventory()
    {
        _inventory.Clear();
        _dataSets.Clear();
    }
}
