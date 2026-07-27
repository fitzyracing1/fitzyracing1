using AspectControlUnit.Aspects;
using AspectControlUnit.Models;
using Xunit;

namespace AspectControlUnit.Tests;

public class WebcamCaptureAspectTests
{
    [Fact]
    public async Task ExecuteAsync_ShouldCaptureFrame()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-1",
            "Test Webcam Capture",
            deviceId: "test-device",
            width: 640,
            height: 480);

        // Act
        var result = await aspect.ExecuteAsync();

        // Assert
        Assert.NotNull(result);
        Assert.True(result.Success);
        Assert.Contains("Captured frame", result.Message);
        Assert.NotNull(result.Data);
        Assert.IsType<WebcamFrame>(result.Data);
    }

    [Fact]
    public async Task ExecuteAsync_ShouldCreateValidFrame()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-2",
            "Frame Validation Test",
            width: 1280,
            height: 720);

        // Act
        var result = await aspect.ExecuteAsync();
        var frame = result.Data as WebcamFrame;

        // Assert
        Assert.NotNull(frame);
        Assert.Equal(1280, frame.Width);
        Assert.Equal(720, frame.Height);
        Assert.NotNull(frame.FrameData);
        Assert.True(frame.FrameData.Length > 0);
        Assert.Equal("JPEG", frame.Format);
        Assert.NotEmpty(frame.FrameId);
    }

    [Fact]
    public async Task VerifyAsync_WithoutCapture_ShouldFail()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-3",
            "Verify Without Capture");

        // Act
        var result = await aspect.VerifyAsync();

        // Assert
        Assert.False(result);
    }

    [Fact]
    public async Task VerifyAsync_AfterCapture_ShouldSucceed()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-4",
            "Verify After Capture",
            width: 800,
            height: 600);

        // Act
        await aspect.ExecuteAsync();
        var result = await aspect.VerifyAsync();

        // Assert
        Assert.True(result);
    }

    [Fact]
    public async Task GetLastFrame_ShouldReturnCapturedFrame()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-5",
            "Last Frame Test");

        // Act
        await aspect.ExecuteAsync();
        var lastFrame = aspect.GetLastFrame();

        // Assert
        Assert.NotNull(lastFrame);
        Assert.NotNull(lastFrame.FrameData);
        Assert.True(lastFrame.SizeInBytes > 0);
    }

    [Fact]
    public async Task CaptureMultipleFramesAsync_ShouldCaptureRequestedCount()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-6",
            "Multiple Frames Test");
        var frameCount = 3;

        // Act
        var frames = await aspect.CaptureMultipleFramesAsync(frameCount, delayMs: 50);

        // Assert
        Assert.Equal(frameCount, frames.Count);
        Assert.All(frames, frame =>
        {
            Assert.NotNull(frame.FrameData);
            Assert.True(frame.FrameData.Length > 0);
        });
    }

    [Fact]
    public async Task WebcamFrame_ShouldHaveMetadata()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-7",
            "Metadata Test",
            deviceId: "device-123");

        // Act
        var result = await aspect.ExecuteAsync();
        var frame = result.Data as WebcamFrame;

        // Assert
        Assert.NotNull(frame);
        Assert.NotNull(frame.Metadata);
        Assert.True(frame.Metadata.ContainsKey("AspectRatio"));
        Assert.True(frame.Metadata.ContainsKey("CaptureMode"));
        Assert.Equal("device-123", frame.DeviceId);
    }

    [Fact]
    public async Task ExecuteAsync_WithOutputPath_ShouldSaveFile()
    {
        // Arrange
        var outputPath = Path.Combine(Path.GetTempPath(), "webcam_test");
        var aspect = new WebcamCaptureAspect(
            "webcam-8",
            "File Save Test",
            outputPath: outputPath);

        try
        {
            // Act
            var result = await aspect.ExecuteAsync();
            var frame = result.Data as WebcamFrame;

            // Assert
            Assert.NotNull(frame);
            Assert.NotNull(frame.FilePath);
            Assert.True(File.Exists(frame.FilePath));
        }
        finally
        {
            // Cleanup
            if (Directory.Exists(outputPath))
            {
                Directory.Delete(outputPath, true);
            }
        }
    }

    [Fact]
    public async Task WebcamFrame_ShouldHaveUniqueIds()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-9",
            "Unique ID Test");

        // Act
        var frames = await aspect.CaptureMultipleFramesAsync(5);
        var frameIds = frames.Select(f => f.FrameId).ToList();

        // Assert
        Assert.Equal(frameIds.Count, frameIds.Distinct().Count());
    }

    [Fact]
    public async Task WebcamFrame_ShouldHaveTimestamp()
    {
        // Arrange
        var aspect = new WebcamCaptureAspect(
            "webcam-10",
            "Timestamp Test");
        var beforeCapture = DateTime.UtcNow.AddSeconds(-1);

        // Act
        var result = await aspect.ExecuteAsync();
        var frame = result.Data as WebcamFrame;
        var afterCapture = DateTime.UtcNow.AddSeconds(1);

        // Assert
        Assert.NotNull(frame);
        Assert.InRange(frame.CapturedAt, beforeCapture, afterCapture);
    }
}
