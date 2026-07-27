# Aspect Control Unit

A C# library that implements a compute difference aspect control unit for managing and verifying all aspects of unit tasks.

## Features

- **Aspect-Based Architecture**: Modular design for managing different aspects of tasks
- **Compute Difference**: Built-in aspect for computing numerical differences
- **Comprehensive Testing**: Full unit test and system function test coverage
- **Verification System**: Built-in verification for all aspects

## Project Structure

```
aspect/
├── src/
│   └── AspectControlUnit/
│       ├── Aspects/          # Aspect implementations
│       ├── Core/             # Core control unit logic
│       ├── Interfaces/       # Interface definitions
│       └── Models/           # Data models
├── tests/
│   └── AspectControlUnit.Tests/
│       ├── AspectControlUnitTests.cs
│       ├── ComputeDifferenceAspectTests.cs
│       └── SystemFunctionTests.cs
└── AspectControlUnit.sln
```

## Requirements

- .NET SDK 8.0 or later

## Building the Project

```powershell
dotnet restore
dotnet build
```

## Running Tests

```powershell
# Run all tests
dotnet test

# Run with detailed output
dotnet test --verbosity normal

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

## Additional Tools

### Python Algorithm Checker
Validates the compute difference algorithm with comprehensive test cases:

```powershell
python algorithm_check.py
```

### Ada Data Distributor
Distributes computation data and reports algorithm usage. Requires GNAT Ada compiler:

```powershell
# Compile (requires GNAT Ada compiler)
gnatmake data_distributor.adb

# Run
.\data_distributor
```

**Note:** The Ada file is provided but requires the GNAT Ada compiler to be installed. Download from: https://www.adacore.com/download

## Running the Complete Pipeline

The project includes a complete executable pipeline that processes inventory data through a prime game and distributes to Unreal Engine:

```powershell
# Run the full pipeline
dotnet run --project src\AspectControlUnit.Runner\AspectControlUnit.Runner.csproj
```

This will:
1. **Populate Inventory** with 10 items (prime data blocks and resource packs)
2. **Create DataSets** from inventory by category
3. **Process through Prime Game** to identify prime numbers and calculate scores
4. **Distribute to Unreal Engine** by exporting JSON files to `UnrealExport/` directory
5. Display complete pipeline statistics

## AI Results Web Search Viewer

The `web-viewer` app now includes an AI Results tab that:
- Displays a 3% sample from `algorithm_check_results.json` (rounded up, min 1)
- Provides authoritative references for the remaining topics
- Optionally performs live web searches via Bing API

### Run the Web Viewer

```powershell
cd .\web-viewer
npm install
npm run dev
```

Open the local URL printed by Vite (e.g., `http://localhost:5173`).

### Enable Live Web Search (Optional)

```powershell
$env:VITE_BING_SEARCH_KEY = "<YOUR_BING_SEARCH_API_KEY>"; npm run dev
```

Notes:
- Without a Bing key, the app shows curated Microsoft Docs and standards links.
- The data file `web-viewer/public/algorithm_check_results.json` is used by the viewer.
- Topics include numeric types, IEEE 754, Infinity/NaN, decimal vs double, BigInteger/overflow, mixed-sign arithmetic, and JSON handling.

## Usage Example

```csharp
using AspectControlUnit.Core;
using AspectControlUnit.Aspects;

// Create control unit
var controlUnit = new AspectControlUnit();

// Register aspects
var aspect1 = new ComputeDifferenceAspect("diff-1", "Difference Aspect", 100, 25);
controlUnit.RegisterAspect(aspect1);

// Execute all aspects
var results = await controlUnit.ExecuteAllAspectsAsync();

// Verify all aspects
var verified = await controlUnit.VerifyAllAspectsAsync();

// Get results
var allResults = controlUnit.GetResults();
```

## Architecture

### Core Components

- **AspectControlUnit**: Main control unit managing aspect execution and verification
- **IAspect**: Interface defining aspect contract
- **AspectResult**: Result model for aspect execution
- **ComputeDifference**: Model for difference computation

### Aspects

- **ComputeDifferenceAspect**: Computes numerical differences between two values

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Test individual components in isolation
- **System Function Tests**: Test integrated system behavior
- **Theory Tests**: Parameterized tests for various input scenarios

## License

This project is open source.
