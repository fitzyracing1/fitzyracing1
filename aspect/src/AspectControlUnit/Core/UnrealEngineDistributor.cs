namespace AspectControlUnit.Core;

/// <summary>
/// Distributes data to Unreal Engine via JSON export
/// </summary>
public class UnrealEngineDistributor
{
    private readonly string _outputDirectory;

    public UnrealEngineDistributor(string outputDirectory = "UnrealExport")
    {
        _outputDirectory = outputDirectory;
        Directory.CreateDirectory(_outputDirectory);
    }

    public string DistributeData(object data, string filename)
    {
        var json = System.Text.Json.JsonSerializer.Serialize(data, new System.Text.Json.JsonSerializerOptions
        {
            WriteIndented = true
        });

        var filePath = Path.Combine(_outputDirectory, filename);
        File.WriteAllText(filePath, json);

        return filePath;
    }

    public string DistributePrimeGameState(Models.PrimeGameState state)
    {
        return DistributeData(state, $"PrimeGame_{DateTime.UtcNow:yyyyMMddHHmmss}.json");
    }

    public string DistributeDataSet(Models.DataSet dataSet)
    {
        return DistributeData(dataSet, $"DataSet_{dataSet.Id}.json");
    }

    public string DistributeInventory(List<Models.InventoryItem> inventory)
    {
        return DistributeData(inventory, $"Inventory_{DateTime.UtcNow:yyyyMMddHHmmss}.json");
    }

    public List<string> GetDistributedFiles()
    {
        return Directory.GetFiles(_outputDirectory, "*.json").ToList();
    }

    public void ClearDistributions()
    {
        foreach (var file in Directory.GetFiles(_outputDirectory, "*.json"))
        {
            File.Delete(file);
        }
    }
}
