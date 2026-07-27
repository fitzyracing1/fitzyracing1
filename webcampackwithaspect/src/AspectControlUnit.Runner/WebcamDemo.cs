using AspectControlUnit.Aspects;
using AspectControlUnit.Models;

namespace AspectControlUnit.Runner;

/// <summary>
/// Demonstrates webcam capture aspect functionality
/// </summary>
public class WebcamDemo
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== Webcam Capture Aspect Demo ===\n");

        // Create output directory
        var outputPath = Path.Combine(Directory.GetCurrentDirectory(), "WebcamCaptures");

        // Demo 1: Single frame capture
        await DemoSingleCapture(outputPath);

        Console.WriteLine();

        // Demo 2: Multiple frame capture
        await DemoMultipleCapture(outputPath);

        Console.WriteLine();

        // Demo 3: Frame verification
        await DemoFrameVerification();

        Console.WriteLine($"\n✓ All webcam demos completed successfully!");
        Console.WriteLine($"✓ Captured frames saved to: {outputPath}");
    }

    private static async Task DemoSingleCapture(string outputPath)
    {
        Console.WriteLine("--- Demo 1: Single Frame Capture ---");

        var webcamAspect = new WebcamCaptureAspect(
            id: "webcam-demo-1",
            name: "Demo Webcam Single",
            deviceId: "primary-camera",
            width: 1280,
            height: 720,
            outputPath: outputPath
        );

        var result = await webcamAspect.ExecuteAsync();

        if (result.Success && result.Data is WebcamFrame frame)
        {
            Console.WriteLine($"✓ Captured frame: {frame.FrameId}");
            Console.WriteLine($"  Resolution: {frame.Width}x{frame.Height}");
            Console.WriteLine($"  Format: {frame.Format}");
            Console.WriteLine($"  Size: {frame.SizeInBytes:N0} bytes");
            Console.WriteLine($"  Timestamp: {frame.CapturedAt:yyyy-MM-dd HH:mm:ss}");
            Console.WriteLine($"  Saved to: {frame.FilePath}");

            if (frame.Metadata.Count > 0)
            {
                Console.WriteLine("  Metadata:");
                foreach (var (key, value) in frame.Metadata)
                {
                    Console.WriteLine($"    - {key}: {value}");
                }
            }
        }
        else
        {
            Console.WriteLine($"✗ Failed: {result.Message}");
        }
    }

    private static async Task DemoMultipleCapture(string outputPath)
    {
        Console.WriteLine("--- Demo 2: Multiple Frame Capture ---");

        var webcamAspect = new WebcamCaptureAspect(
            id: "webcam-demo-2",
            name: "Demo Webcam Burst",
            deviceId: "primary-camera",
            width: 640,
            height: 480,
            outputPath: outputPath
        );

        var frameCount = 5;
        Console.WriteLine($"Capturing {frameCount} frames with 200ms delay...");

        var frames = await webcamAspect.CaptureMultipleFramesAsync(frameCount, delayMs: 200);

        Console.WriteLine($"✓ Captured {frames.Count} frames:");
        for (int i = 0; i < frames.Count; i++)
        {
            var frame = frames[i];
            Console.WriteLine($"  Frame {i + 1}: {frame.FrameId} ({frame.SizeInBytes:N0} bytes)");
        }

        // Calculate total size
        var totalSize = frames.Sum(f => f.SizeInBytes);
        Console.WriteLine($"  Total size: {totalSize:N0} bytes");
    }

    private static async Task DemoFrameVerification()
    {
        Console.WriteLine("--- Demo 3: Frame Verification ---");

        var webcamAspect = new WebcamCaptureAspect(
            id: "webcam-demo-3",
            name: "Demo Webcam Verify",
            width: 1920,
            height: 1080
        );

        // Try to verify before capture (should fail)
        Console.WriteLine("Verifying before capture...");
        var verifyBefore = await webcamAspect.VerifyAsync();
        Console.WriteLine($"  Result: {(verifyBefore ? "✓ Valid" : "✗ Invalid (expected)")}");

        // Capture a frame
        Console.WriteLine("Capturing frame...");
        var captureResult = await webcamAspect.ExecuteAsync();
        Console.WriteLine($"  Capture: {(captureResult.Success ? "✓ Success" : "✗ Failed")}");

        // Verify after capture (should succeed)
        Console.WriteLine("Verifying after capture...");
        var verifyAfter = await webcamAspect.VerifyAsync();
        Console.WriteLine($"  Result: {(verifyAfter ? "✓ Valid" : "✗ Invalid")}");

        // Get last frame details
        var lastFrame = webcamAspect.GetLastFrame();
        if (lastFrame != null)
        {
            Console.WriteLine($"  Last frame: {lastFrame.Width}x{lastFrame.Height}, {lastFrame.SizeInBytes:N0} bytes");
        }
    }
}
