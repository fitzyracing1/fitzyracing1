// Unreal Engine Blueprint Import Script
// Place this in your Unreal Engine project Content folder
// This can be used as reference for creating Blueprint nodes

/*
=============================================================================
UNREAL ENGINE JSON DATA IMPORTER
=============================================================================
This script demonstrates how to import and parse the JSON files generated
by the Aspect Control Unit pipeline.

BLUEPRINT NODE SETUP:
=============================================================================

1. LOAD JSON FILE
   - Use "Load File to String" node
   - File Path: "../../../aspect/UnrealExport/[filename].json"
   
2. PARSE JSON
   - Use "Json Object from String" node
   - Connect the loaded string output
   
3. EXTRACT DATA FIELDS
   - Use "Get Field" nodes to extract specific values
   
=============================================================================
*/

// Example C++ Header (MyDataImporter.h)
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "JsonObjectConverter.h"
#include "MyDataImporter.generated.h"

// Inventory Item Structure
USTRUCT(BlueprintType)
struct FInventoryItem
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Inventory")
    FString Id;

    UPROPERTY(BlueprintReadWrite, Category = "Inventory")
    FString Name;

    UPROPERTY(BlueprintReadWrite, Category = "Inventory")
    float Value;

    UPROPERTY(BlueprintReadWrite, Category = "Inventory")
    FString Category;

    UPROPERTY(BlueprintReadWrite, Category = "Inventory")
    FString CreatedAt;
};

// Prime Game State Structure
USTRUCT(BlueprintType)
struct FPrimeGameState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "PrimeGame")
    int32 CurrentNumber;

    UPROPERTY(BlueprintReadWrite, Category = "PrimeGame")
    bool IsPrime;

    UPROPERTY(BlueprintReadWrite, Category = "PrimeGame")
    int32 Score;

    UPROPERTY(BlueprintReadWrite, Category = "PrimeGame")
    TArray<int32> PrimesFound;

    UPROPERTY(BlueprintReadWrite, Category = "PrimeGame")
    FString LastUpdated;
};

// DataSet Structure
USTRUCT(BlueprintType)
struct FDataSet
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "DataSet")
    FString Id;

    UPROPERTY(BlueprintReadWrite, Category = "DataSet")
    TArray<float> Values;

    UPROPERTY(BlueprintReadWrite, Category = "DataSet")
    FString Source;

    UPROPERTY(BlueprintReadWrite, Category = "DataSet")
    FString Timestamp;
};

// Main Importer Actor
UCLASS()
class YOURGAME_API AMyDataImporter : public AActor
{
    GENERATED_BODY()

public:
    AMyDataImporter();

    // Blueprint callable functions
    UFUNCTION(BlueprintCallable, Category = "DataImport")
    bool LoadInventoryData(const FString& FilePath, TArray<FInventoryItem>& OutInventory);

    UFUNCTION(BlueprintCallable, Category = "DataImport")
    bool LoadPrimeGameState(const FString& FilePath, FPrimeGameState& OutGameState);

    UFUNCTION(BlueprintCallable, Category = "DataImport")
    bool LoadDataSet(const FString& FilePath, FDataSet& OutDataSet);

    UFUNCTION(BlueprintCallable, Category = "DataImport")
    FString GetProjectDirectory();

private:
    FString LoadJsonFromFile(const FString& FilePath);
};


// Example C++ Implementation (MyDataImporter.cpp)
/*
#include "MyDataImporter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "JsonUtilities.h"

AMyDataImporter::AMyDataImporter()
{
    PrimaryActorTick.bCanEverTick = false;
}

FString AMyDataImporter::LoadJsonFromFile(const FString& FilePath)
{
    FString JsonString;
    FString FullPath = FPaths::ProjectDir() + FilePath;
    
    if (FFileHelper::LoadFileToString(JsonString, *FullPath))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded JSON from: %s"), *FullPath);
        return JsonString;
    }
    
    UE_LOG(LogTemp, Error, TEXT("Failed to load JSON from: %s"), *FullPath);
    return FString();
}

bool AMyDataImporter::LoadInventoryData(const FString& FilePath, TArray<FInventoryItem>& OutInventory)
{
    FString JsonString = LoadJsonFromFile(FilePath);
    if (JsonString.IsEmpty()) return false;

    return FJsonObjectConverter::JsonArrayStringToUStruct(JsonString, &OutInventory, 0, 0);
}

bool AMyDataImporter::LoadPrimeGameState(const FString& FilePath, FPrimeGameState& OutGameState)
{
    FString JsonString = LoadJsonFromFile(FilePath);
    if (JsonString.IsEmpty()) return false;

    return FJsonObjectConverter::JsonObjectStringToUStruct(JsonString, &OutGameState, 0, 0);
}

bool AMyDataImporter::LoadDataSet(const FString& FilePath, FDataSet& OutDataSet)
{
    FString JsonString = LoadJsonFromFile(FilePath);
    if (JsonString.IsEmpty()) return false;

    return FJsonObjectConverter::JsonObjectStringToUStruct(JsonString, &OutDataSet, 0, 0);
}

FString AMyDataImporter::GetProjectDirectory()
{
    return FPaths::ProjectDir();
}
*/


/*
=============================================================================
BLUEPRINT USAGE EXAMPLE:
=============================================================================

1. CREATE BLUEPRINT:
   - Create new Blueprint Class based on "MyDataImporter"
   - Name it "BP_DataImporter"

2. LOAD INVENTORY:
   Event BeginPlay
   → Get Actor of Class (MyDataImporter)
   → Load Inventory Data
      File Path: "../../../aspect/UnrealExport/Inventory_20251124000004.json"
   → ForEach Loop (on OutInventory array)
      → Print String (display Name and Value)

3. LOAD PRIME GAME STATE:
   → Load Prime Game State
      File Path: "../../../aspect/UnrealExport/PrimeGame_20251124000004.json"
   → Print String (Score: {OutGameState.Score})
   → ForEach Loop (on PrimesFound array)
      → Print String (display each prime number)

4. LOAD DATASET:
   → Load Data Set
      File Path: "../../../aspect/UnrealExport/DataSet_[guid].json"
   → ForEach Loop (on Values array)
      → Print String (display each value)

=============================================================================
VISUAL SCRIPTING (BLUEPRINT NODES):
=============================================================================

[Event BeginPlay]
    |
    v
[Load File to String]
    Path: "C:/Users/EC/aspect/UnrealExport/PrimeGame_20251124000004.json"
    |
    v
[Parse JSON]
    |
    v
[Get JSON Field: "Score"]
    |
    v
[Print String] "Prime Game Score: {Score}"
    |
    v
[Get JSON Field: "PrimesFound"]
    |
    v
[ForEach Loop]
    |
    v
[Print String] "Prime Number: {ArrayElement}"

=============================================================================
EXAMPLE PATHS (Update with your actual file names):
=============================================================================
*/

// Inventory File
const FString InventoryPath = TEXT("../../../aspect/UnrealExport/Inventory_20251124000004.json");

// Prime Game State File
const FString PrimeGamePath = TEXT("../../../aspect/UnrealExport/PrimeGame_20251124000004.json");

// DataSet Files (use actual GUIDs from your files)
const FString DataSetPath1 = TEXT("../../../aspect/UnrealExport/DataSet_66b5e9d0-0162-42a3-a875-4002bede3a1c.json");
const FString DataSetPath2 = TEXT("../../../aspect/UnrealExport/DataSet_1be6b589-4209-469c-8fef-ee7544ebd65a.json");

/*
=============================================================================
EXPECTED DATA FORMAT:
=============================================================================

INVENTORY JSON:
[
  {
    "Id": "ITM001",
    "Name": "Data Block Alpha",
    "Value": 17.0,
    "Category": "Prime",
    "CreatedAt": "2025-11-24T00:00:04.6263137Z"
  }
]

PRIME GAME STATE JSON:
{
  "CurrentNumber": 200,
  "IsPrime": false,
  "Score": 221,
  "PrimesFound": [17, 23, 29, 31, 37, 41, 43],
  "LastUpdated": "2025-11-24T00:00:04.6263137Z"
}

DATASET JSON:
{
  "Id": "66b5e9d0-0162-42a3-a875-4002bede3a1c",
  "Values": [17.0, 23.0, 29.0, 31.0, 37.0, 41.0, 43.0],
  "Source": "Inventory-Prime",
  "Timestamp": "2025-11-24T00:00:04.6263137Z"
}

=============================================================================
NOTES:
=============================================================================
- Add "Json" and "JsonUtilities" modules to YourGame.Build.cs
- Update file paths to match your actual exported files
- Consider using relative paths from project directory
- Handle JSON parsing errors with proper error checking
=============================================================================
*/
