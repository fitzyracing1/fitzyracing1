# Webcam Capture Quick Start Guide

## Overview

The Aspect Control Unit now includes webcam capture functionality through the `WebcamCaptureAspect` class. This guide will help you get started with capturing and managing webcam frames.

## Basic Usage

### 1. Create a Webcam Aspect

```csharp
using AspectControlUnit.Aspects;
using AspectControlUnit.Models;

var webcamAspect = new WebcamCaptureAspect(
    id: "webcam-1",
    name: "My Webcam",
    deviceId: "default",
    width: 1280,
    height: 720,
    outputPath: "./captures"  // Optional: saves frames to disk
);
```

### 2. Capture a Single Frame

```csharp
var result = await webcamAspect.ExecuteAsync();

if (result.Success && result.Data is WebcamFrame frame)
{
    Console.WriteLine($"Frame ID: {frame.FrameId}");
    Console.WriteLine($"Size: {frame.Width}x{frame.Height}");
    Console.WriteLine($"Bytes: {frame.SizeInBytes}");
    Console.WriteLine($"File: {frame.FilePath}");
}
```

### 3. Capture Multiple Frames

```csharp
var frames = await webcamAspect.CaptureMultipleFramesAsync(
    count: 10,
    delayMs: 100  // 100ms between frames
);

foreach (var frame in frames)
{
    Console.WriteLine($"Captured: {frame.FrameId} at {frame.CapturedAt}");
}
```

### 4. Verify Frame Integrity

```csharp
await webcamAspect.ExecuteAsync();
bool isValid = await webcamAspect.VerifyAsync();

if (isValid)
{
    Console.WriteLine("Frame is valid!");
}
```

## WebcamFrame Properties

| Property | Type | Description |
|----------|------|-------------|
| `FrameId` | `string` | Unique identifier for the frame |
| `CapturedAt` | `DateTime` | Timestamp when frame was captured |
| `Width` | `int` | Frame width in pixels |
| `Height` | `int` | Frame height in pixels |
| `FrameData` | `byte[]` | Raw image data (JPEG format) |
| `Format` | `string` | Image format (e.g., "JPEG") |
| `DeviceId` | `string` | Camera device identifier |
| `FilePath` | `string?` | Path if saved to disk |
| `Metadata` | `Dictionary<string,string>` | Additional frame metadata |
| `SizeInBytes` | `long` | Total size of frame data |

## Common Scenarios

### Scenario 1: Time-Lapse Capture

```csharp
var webcam = new WebcamCaptureAspect("timelapse", "Time Lapse", 
    outputPath: "./timelapse");

// Capture one frame every 5 seconds for 1 minute
for (int i = 0; i < 12; i++)
{
    await webcam.ExecuteAsync();
    await Task.Delay(5000);
}
```

### Scenario 2: Quality Monitoring

```csharp
var webcam = new WebcamCaptureAspect("monitor", "Quality Monitor");

var result = await webcam.ExecuteAsync();
var frame = result.Data as WebcamFrame;

// Check frame quality
if (frame.SizeInBytes < 10000)
{
    Console.WriteLine("Warning: Frame size is unusually small");
}

// Verify dimensions
bool valid = await webcam.VerifyAsync();
if (!valid)
{
    Console.WriteLine("Frame validation failed");
}
```

### Scenario 3: Burst Capture with Analysis

```csharp
var webcam = new WebcamCaptureAspect("burst", "Burst Capture", 
    width: 1920, height: 1080);

// Capture burst
var frames = await webcam.CaptureMultipleFramesAsync(20, delayMs: 50);

// Analyze
var avgSize = frames.Average(f => f.SizeInBytes);
var timestamps = frames.Select(f => f.CapturedAt).ToList();
var duration = timestamps.Last() - timestamps.First();

Console.WriteLine($"Captured {frames.Count} frames in {duration.TotalSeconds:F2}s");
Console.WriteLine($"Average frame size: {avgSize:N0} bytes");
```

## Running the Demo

To see the webcam capture in action:

```powershell
dotnet run --project src\AspectControlUnit.Runner\AspectControlUnit.Runner.csproj
```

Then select option 2 (Webcam Capture Demo) from the menu.

## Testing

Run the comprehensive webcam test suite:

```powershell
dotnet test --filter "WebcamCaptureAspectTests"
```

## Notes

- The current implementation generates simulated frames with gradients and timestamps
- For production use with real webcams, integrate libraries like:
  - **OpenCvSharp** - Cross-platform webcam access
  - **AForge.NET** - Windows DirectShow support
  - **Emgu.CV** - .NET wrapper for OpenCV
- Frame data is stored as JPEG-encoded byte arrays
- All captured frames include metadata about aspect ratio and capture mode
- The `outputPath` parameter is optional; omit it to keep frames in memory only

## Integration with Existing Pipeline

The webcam aspect integrates seamlessly with the existing Aspect Control Unit:

```csharp
using AspectControlUnit.Core;
using AspectControlUnit.Aspects;

var controlUnit = new Core.AspectControlUnit();

// Add webcam aspect alongside other aspects
var webcamAspect = new WebcamCaptureAspect("webcam-1", "Pipeline Webcam");
var computeAspect = new ComputeDifferenceAspect("compute-1", "Difference", 100, 50);

// Register and execute
controlUnit.RegisterAspect(webcamAspect);
controlUnit.RegisterAspect(computeAspect);

await controlUnit.ExecuteAllAsync();
```

## Support

For issues or questions:
- Review the test cases in `tests/AspectControlUnit.Tests/WebcamCaptureAspectTests.cs`
- Check the demo implementation in `src/AspectControlUnit.Runner/WebcamDemo.cs`
- Refer to the main README.md for general project information
