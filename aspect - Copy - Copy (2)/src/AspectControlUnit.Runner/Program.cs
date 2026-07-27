using AspectControlUnit.Core;
using AspectControlUnit.Models;

namespace AspectControlUnit.Runner;

/// <summary>
/// Main runner application for Aspect Control Unit
/// Processes inventory data through prime game and distributes to Unreal Engine
/// </summary>
class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================================================");
        Console.WriteLine("ASPECT CONTROL UNIT - INVENTORY TO UNREAL ENGINE PIPELINE");
        Console.WriteLine("========================================================================");
        Console.WriteLine();

        // Initialize components
        var inventoryManager = new InventoryManager();
        var primeGame = new PrimeGameEngine();
        var unrealDistributor = new UnrealEngineDistributor();

        // Step 1: Populate Inventory
        Console.WriteLine("STEP 1: POPULATING INVENTORY");
        Console.WriteLine("----------------------------------------");
        
        var items = new[]
        {
            new InventoryItem { Id = "ITM001", Name = "Data Block Alpha", Value = 17, Category = "Prime" },
            new InventoryItem { Id = "ITM002", Name = "Data Block Beta", Value = 23, Category = "Prime" },
            new InventoryItem { Id = "ITM003", Name = "Data Block Gamma", Value = 29, Category = "Prime" },
            new InventoryItem { Id = "ITM004", Name = "Data Block Delta", Value = 31, Category = "Prime" },
            new InventoryItem { Id = "ITM005", Name = "Resource Pack 1", Value = 100, Category = "Resource" },
            new InventoryItem { Id = "ITM006", Name = "Resource Pack 2", Value = 150, Category = "Resource" },
            new InventoryItem { Id = "ITM007", Name = "Data Block Epsilon", Value = 37, Category = "Prime" },
            new InventoryItem { Id = "ITM008", Name = "Data Block Zeta", Value = 41, Category = "Prime" },
            new InventoryItem { Id = "ITM009", Name = "Resource Pack 3", Value = 200, Category = "Resource" },
            new InventoryItem { Id = "ITM010", Name = "Data Block Theta", Value = 43, Category = "Prime" }
        };

        foreach (var item in items)
        {
            inventoryManager.AddItem(item);
            Console.WriteLine($"  Added: {item.Name} (Value: {item.Value}, Category: {item.Category})");
        }

        Console.WriteLine($"\nTotal Inventory Items: {inventoryManager.GetInventoryCount()}");
        Console.WriteLine();

        // Step 2: Create DataSets from Inventory
        Console.WriteLine("STEP 2: CREATING DATASETS FROM INVENTORY");
        Console.WriteLine("----------------------------------------");

        var primeDataSet = inventoryManager.CreateDataSetFromInventory("Prime");
        Console.WriteLine($"Created Prime DataSet: {primeDataSet.Id}");
        Console.WriteLine($"  Values: {string.Join(", ", primeDataSet.Values)}");

        var resourceDataSet = inventoryManager.CreateDataSetFromInventory("Resource");
        Console.WriteLine($"Created Resource DataSet: {resourceDataSet.Id}");
        Console.WriteLine($"  Values: {string.Join(", ", resourceDataSet.Values)}");
        Console.WriteLine();

        // Step 3: Process through Prime Game
        Console.WriteLine("STEP 3: PROCESSING DATA THROUGH PRIME GAME ENGINE");
        Console.WriteLine("----------------------------------------");

        var gameState = primeGame.ProcessDataSet(primeDataSet);
        Console.WriteLine($"Processed {primeDataSet.Values.Count} values from Prime DataSet");
        Console.WriteLine($"  Primes Found: {string.Join(", ", gameState.PrimesFound)}");
        Console.WriteLine($"  Game Score: {gameState.Score}");
        Console.WriteLine();

        // Process resource dataset
        gameState = primeGame.ProcessDataSet(resourceDataSet);
        Console.WriteLine($"Processed {resourceDataSet.Values.Count} values from Resource DataSet");
        Console.WriteLine($"  Total Primes Found: {gameState.PrimesFound.Count}");
        Console.WriteLine($"  Total Game Score: {gameState.Score}");
        Console.WriteLine();

        // Step 4: Distribute to Unreal Engine
        Console.WriteLine("STEP 4: DISTRIBUTING TO UNREAL ENGINE");
        Console.WriteLine("----------------------------------------");

        var inventoryPath = unrealDistributor.DistributeInventory(inventoryManager.GetInventory());
        Console.WriteLine($"✓ Distributed Inventory: {inventoryPath}");

        var primeDataPath = unrealDistributor.DistributeDataSet(primeDataSet);
        Console.WriteLine($"✓ Distributed Prime DataSet: {primeDataPath}");

        var resourceDataPath = unrealDistributor.DistributeDataSet(resourceDataSet);
        Console.WriteLine($"✓ Distributed Resource DataSet: {resourceDataPath}");

        var gameStatePath = unrealDistributor.DistributePrimeGameState(gameState);
        Console.WriteLine($"✓ Distributed Prime Game State: {gameStatePath}");
        Console.WriteLine();

        // Step 5: Summary
        Console.WriteLine("STEP 5: PIPELINE SUMMARY");
        Console.WriteLine("----------------------------------------");
        Console.WriteLine($"Inventory Items Processed: {inventoryManager.GetInventoryCount()}");
        Console.WriteLine($"DataSets Created: 2");
        Console.WriteLine($"Prime Numbers Identified: {gameState.PrimesFound.Count}");
        Console.WriteLine($"Final Game Score: {gameState.Score}");
        Console.WriteLine($"Files Distributed to Unreal: {unrealDistributor.GetDistributedFiles().Count}");
        Console.WriteLine();

        Console.WriteLine("========================================================================");
        Console.WriteLine("✓ PIPELINE EXECUTION COMPLETED SUCCESSFULLY");
        Console.WriteLine("========================================================================");
        Console.WriteLine();
        Console.WriteLine("Unreal Engine can now import JSON files from: ./UnrealExport/");
    }
}
