namespace AspectControlUnit.Interfaces;

/// <summary>
/// Represents a single aspect of a unit task
/// </summary>
public interface IAspect
{
    /// <summary>
    /// Unique identifier for the aspect
    /// </summary>
    string Id { get; }

    /// <summary>
    /// Name of the aspect
    /// </summary>
    string Name { get; }

    /// <summary>
    /// Execute the aspect logic
    /// </summary>
    /// <returns>Result of the aspect execution</returns>
    Task<AspectResult> ExecuteAsync();

    /// <summary>
    /// Verify the aspect execution
    /// </summary>
    /// <returns>True if verification passed</returns>
    Task<bool> VerifyAsync();
}
