using AspectControlUnit.Interfaces;
using AspectControlUnit.Models;
using System.Drawing;
using System.Drawing.Imaging;

namespace AspectControlUnit.Aspects;

/// <summary>
/// Aspect that handles webcam capture functionality
/// </summary>
public class WebcamCaptureAspect : IAspect
{
    private readonly string _deviceId;
    private readonly int _width;
    private readonly int _height;
    private readonly string? _outputPath;
    private WebcamFrame? _lastFrame;

    public string Id { get; }
    public string Name { get; }

    public WebcamCaptureAspect(
        string id, 
        string name, 
        string deviceId = "default", 
        int width = 1280, 
        int height = 720,
        string? outputPath = null)
    {
        Id = id;
        Name = name;
        _deviceId = deviceId;
        _width = width;
        _height = height;
        _outputPath = outputPath;
    }

    public async Task<AspectResult> ExecuteAsync()
    {
        try
        {
            // Simulate webcam frame capture
            // In a real implementation, this would interface with a webcam library
            var frame = await CaptureFrameAsync();

            _lastFrame = frame;

            return new AspectResult
            {
                AspectId = Id,
                Success = true,
                Message = $"Captured frame {frame.FrameId} from device {_deviceId}",
                Data = frame
            };
        }
        catch (Exception ex)
        {
            return new AspectResult
            {
                AspectId = Id,
                Success = false,
                Message = $"Failed to capture webcam frame: {ex.Message}",
                Data = null
            };
        }
    }

    public async Task<bool> VerifyAsync()
    {
        if (_lastFrame == null)
        {
            return false;
        }

        // Verify frame integrity
        bool isValid = _lastFrame.Width == _width &&
                      _lastFrame.Height == _height &&
                      _lastFrame.FrameData != null &&
                      _lastFrame.FrameData.Length > 0;

        return await Task.FromResult(isValid);
    }

    private async Task<WebcamFrame> CaptureFrameAsync()
    {
        // Create a simulated frame capture
        // In production, this would use libraries like:
        // - OpenCvSharp for cross-platform webcam access
        // - DirectShow for Windows
        // - AForge.NET for .NET webcam integration
        
        var frame = new WebcamFrame
        {
            Width = _width,
            Height = _height,
            DeviceId = _deviceId,
            Format = "JPEG",
            CapturedAt = DateTime.UtcNow
        };

        // Simulate frame data (create a simple colored bitmap)
        frame.FrameData = await GenerateSampleFrameDataAsync();

        // Save to file if output path is specified
        if (!string.IsNullOrEmpty(_outputPath))
        {
            var filename = $"webcam_{frame.FrameId}_{DateTime.Now:yyyyMMddHHmmss}.jpg";
            var fullPath = Path.Combine(_outputPath, filename);
            
            Directory.CreateDirectory(_outputPath);
            await File.WriteAllBytesAsync(fullPath, frame.FrameData);
            
            frame.FilePath = fullPath;
            frame.Metadata["SavedTo"] = fullPath;
        }

        frame.Metadata["AspectRatio"] = $"{_width}:{_height}";
        frame.Metadata["CaptureMode"] = "Simulated";

        return frame;
    }

    private async Task<byte[]> GenerateSampleFrameDataAsync()
    {
        // Generate a simple bitmap as sample data
        using var bitmap = new Bitmap(_width, _height);
        using var graphics = Graphics.FromImage(bitmap);
        
        // Fill with a gradient
        using var brush = new System.Drawing.Drawing2D.LinearGradientBrush(
            new Rectangle(0, 0, _width, _height),
            Color.FromArgb(50, 100, 200),
            Color.FromArgb(200, 100, 50),
            45f);
        
        graphics.FillRectangle(brush, 0, 0, _width, _height);

        // Add timestamp text
        var text = $"Webcam Frame - {DateTime.Now:yyyy-MM-dd HH:mm:ss}";
        using var font = new Font("Arial", 20);
        using var textBrush = new SolidBrush(Color.White);
        graphics.DrawString(text, font, textBrush, 10, 10);

        // Convert to byte array
        using var ms = new MemoryStream();
        bitmap.Save(ms, ImageFormat.Jpeg);
        return await Task.FromResult(ms.ToArray());
    }

    /// <summary>
    /// Gets the last captured frame
    /// </summary>
    public WebcamFrame? GetLastFrame() => _lastFrame;

    /// <summary>
    /// Captures multiple frames in sequence
    /// </summary>
    public async Task<List<WebcamFrame>> CaptureMultipleFramesAsync(int count, int delayMs = 100)
    {
        var frames = new List<WebcamFrame>();

        for (int i = 0; i < count; i++)
        {
            var result = await ExecuteAsync();
            if (result.Success && result.Data is WebcamFrame frame)
            {
                frames.Add(frame);
            }

            if (i < count - 1)
            {
                await Task.Delay(delayMs);
            }
        }

        return frames;
    }
}
