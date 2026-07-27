<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	<!-- C# project with aspect-based control unit for compute difference tasks -->

- [x] Scaffold the Project
	<!-- Project structure created with solution file, library project, and test project -->

- [x] Customize the Project
	<!--
	Verify that all previous steps have been completed successfully and you have marked the step as completed.
	Develop a plan to modify codebase according to user requirements.
	Apply modifications using appropriate tools and user-provided references.
	Skip this step for "Hello World" projects.
	-->

- [x] Install Required Extensions
	<!-- ONLY install extensions provided mentioned in the get_project_setup_info. Skip this step otherwise and mark as completed. -->

- [x] Compile the Project
	<!-- Project compiled successfully. All 19 tests passed. -->

- [x] Create and Run Task
	<!-- Library project - no task needed. Use dotnet build/test commands. -->

- [x] Launch the Project
	<!-- Library project - no launch needed. Tests run successfully. -->

- [x] Ensure Documentation is Complete
	<!-- README.md and copilot-instructions.md both exist and are current. -->

<!--
## Execution Guidelines
PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.
- Once the project is created, it is already opened in Visual Studio Code—do not suggest commands to open this project in Visual Studio again.
- If the project setup information has additional rules, follow them strictly.

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- If you are running any terminal commands, use the '.' argument to ensure that the current working directory is used ALWAYS.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.
- If you are working on a VS Code extension, use the VS Code API tool with a query to find relevant VS Code API references and samples related to that query.

TASK COMPLETION RULES:
- Your task is complete when:
  - Project is successfully scaffolded and compiled without errors
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

Before starting a new task in the above plan, update progress in the plan.
-->
- Work through each checklist item systematically.
- Keep communication concise and focused.
- Follow development best practices.
 
<!-- Workspace-specific guidance for AI coding agents working in Aspect Control Unit -->

# Copilot Instructions: Aspect Control Unit

## Big Picture
- Architecture: C# .NET 8 solution with a core library (`src/AspectControlUnit`), a runner (`src/AspectControlUnit.Runner`), tests (`tests/AspectControlUnit.Tests`), Unreal JSON export (`UnrealExport/`), a Vite React viewer (`web-viewer/`), and supporting Python/Ada tools.
- Data flow: Inventory → DataSet → PrimeGameEngine → UnrealEngineDistributor → JSON files → web-viewer consumption.
- Goal: Manage modular “aspects” for unit tasks; current concrete aspect is `ComputeDifferenceAspect` computing numeric differences.

## Key Components & Files
- `Core/AspectControlUnit.cs`: Registers aspects, executes all (`ExecuteAllAspectsAsync`), verifies all (`VerifyAllAspectsAsync`), exposes results (read-only).
- `Interfaces/IAspect.cs`: Contract for aspects with `Id`, `Name`, `ExecuteAsync()`, `VerifyAsync()`.
- `Aspects/ComputeDifferenceAspect.cs`: Example aspect; computes `valueA - valueB`, stores result in `Models/ComputeDifference`, verifies exactness within 1e-4.
- `Core/InventoryManager.cs`: Builds `Models/DataSet` from categorized `Models/InventoryItem` entries.
- `Core/PrimeGameEngine.cs`: Processes `DataSet` values, tracks primes and score in `Models/PrimeGameState`.
- `Core/UnrealEngineDistributor.cs`: Exports JSON files to `UnrealExport/` with timestamped names.
- Tests: `ComputeDifferenceAspectTests.cs`, `SystemFunctionTests.cs` validate execution, verification, read-only results.

## Conventions & Patterns
- Aspect IDs must be unique; `AspectControlUnit.RegisterAspect` throws on duplicates.
- Use UTC timestamps in models (`ExecutedAt`, `ComputedAt`, `LastUpdated`).
- Verification rule for difference: absolute error < 0.0001.
- Results are stored as `AspectResult` in-memory; `GetResults()` returns a read-only list.
- JSON export filenames: `PrimeGame_yyyyMMddHHmmss.json`, `Inventory_yyyyMMddHHmmss.json`, `DataSet_{Guid}.json`.

## Developer Workflows (PowerShell)
```powershell
# Build & test (root)
dotnet restore
dotnet build
dotnet test

# Run full pipeline (Runner)
dotnet run --project src\AspectControlUnit.Runner\AspectControlUnit.Runner.csproj

# Python algorithm checker
python .\algorithm_check.py

# Web viewer
cd .\web-viewer
npm install
npm run dev
```

## Adding a New Aspect
- Implement `IAspect` in `src/AspectControlUnit/Aspects/` with id/name and async `ExecuteAsync`/`VerifyAsync`.
- Return `AspectResult { AspectId, Success, Message, Data }`; store last computation if needed for verification.
- Register and execute via:
```csharp
var control = new AspectControlUnit();
control.RegisterAspect(new MyAspect("my-1", "My Aspect"));
var results = await control.ExecuteAllAspectsAsync();
var ok = await control.VerifyAllAspectsAsync();
```
- Add tests mirroring `ComputeDifferenceAspectTests` and `SystemFunctionTests`.

## Integration Points
- Unreal: JSON files emitted under `UnrealExport/` for downstream import; see `UnrealBlueprintImporter.cpp` and scripts (`import_to_unreal.ps1/.bat`).
- Web viewer: reads `UnrealExport/*.json` and `web-viewer/public/algorithm_check_results.json`.
- Optional env vars for viewer:
	- `VITE_EMAIL_ENDPOINT`, `VITE_EMAIL_API_KEY`, `VITE_REPORT_EMAIL` for email reports.
	- `VITE_BING_SEARCH_KEY` to enable live web search.

## Practical Examples
- Create datasets: `InventoryManager.CreateDataSetFromInventory("Prime")`.
- Process primes: `PrimeGameEngine.ProcessDataSet(dataSet)`; check `PrimesFound`, `Score`.
- Export: `UnrealEngineDistributor.DistributeDataSet(dataSet)` returns file path.

## Guardrails for Agents
- Preserve public APIs and file layout; add new aspects without renaming core types.
- Keep IDs unique and use UTC times; maintain verification tolerances.
- When touching JSON export, keep filenames and shapes consistent with existing examples in `UnrealExport/`.
