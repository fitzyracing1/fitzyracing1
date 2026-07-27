namespace AspectControlUnit.Models;

/// <summary>
/// Represents a captured webcam frame with metadata
/// </summary>
public class WebcamFrame
{
    /// <summary>
    /// Unique identifier for the frame
    /// </summary>
    public string FrameId { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Timestamp when the frame was captured
    /// </summary>
    public DateTime CapturedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Width of the frame in pixels
    /// </summary>
    public int Width { get; set; }

    /// <summary>
    /// Height of the frame in pixels
    /// </summary>
    public int Height { get; set; }

    /// <summary>
    /// Raw frame data (byte array of image data)
    /// </summary>
    public byte[]? FrameData { get; set; }

    /// <summary>
    /// Format of the frame (e.g., "JPEG", "PNG", "BMP")
    /// </summary>
    public string Format { get; set; } = "JPEG";

    /// <summary>
    /// Device ID or name of the webcam
    /// </summary>
    public string DeviceId { get; set; } = string.Empty;

    /// <summary>
    /// Additional metadata about the frame
    /// </summary>
    public Dictionary<string, string> Metadata { get; set; } = new();

    /// <summary>
    /// File path if the frame was saved to disk
    /// </summary>
    public string? FilePath { get; set; }

    /// <summary>
    /// Size of the frame data in bytes
    /// </summary>
    public long SizeInBytes => FrameData?.Length ?? 0;
}
