using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;
using System.Linq;

public class BuildScript
{
    // Build method that can be called from command line
    [MenuItem("Build/Build Windows")]
    public static void BuildWindows()
    {
        BuildGame(BuildTarget.StandaloneWindows64, "Builds/Windows/Game.exe");
    }

    [MenuItem("Build/Build Linux")]
    public static void BuildLinux()
    {
        BuildGame(BuildTarget.StandaloneLinux64, "Builds/Linux/Game");
    }

    [MenuItem("Build/Build macOS")]
    public static void BuildMacOS()
    {
        BuildGame(BuildTarget.StandaloneOSX, "Builds/macOS/Game.app");
    }

    // Command line build method
    public static void PerformBuild()
    {
        string[] args = System.Environment.GetCommandLineArgs();
        
        // Parse command line arguments
        string buildPath = "Builds/Windows/Game.exe";
        BuildTarget buildTarget = BuildTarget.StandaloneWindows64;
        BuildOptions buildOptions = BuildOptions.None;

        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "-buildPath" && i + 1 < args.Length)
            {
                buildPath = args[i + 1];
            }
            else if (args[i] == "-development")
            {
                buildOptions |= BuildOptions.Development;
            }
        }

        BuildGame(buildTarget, buildPath, buildOptions);
    }

    private static void BuildGame(BuildTarget target, string path, BuildOptions options = BuildOptions.None)
    {
        // Get all scenes in build settings
        string[] scenes = EditorBuildSettings.scenes
            .Where(scene => scene.enabled)
            .Select(scene => scene.path)
            .ToArray();

        if (scenes.Length == 0)
        {
            Debug.LogError("No scenes found in Build Settings. Please add scenes to build.");
            EditorApplication.Exit(1);
            return;
        }

        Debug.Log($"Building {target} to {path}");
        Debug.Log($"Scenes: {string.Join(", ", scenes)}");

        // Perform the build
        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = path,
            target = target,
            options = options
        };

        BuildReport report = BuildPipeline.BuildPlayer(buildPlayerOptions);
        BuildSummary summary = report.summary;

        if (summary.result == BuildResult.Succeeded)
        {
            Debug.Log($"Build succeeded: {summary.totalSize} bytes");
            EditorApplication.Exit(0);
        }
        else
        {
            Debug.LogError($"Build failed: {summary.result}");
            EditorApplication.Exit(1);
        }
    }
}
