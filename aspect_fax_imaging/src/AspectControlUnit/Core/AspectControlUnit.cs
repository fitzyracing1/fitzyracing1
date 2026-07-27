using AspectControlUnit.Interfaces;

namespace AspectControlUnit.Core;

/// <summary>
/// Main control unit that manages and delivers all aspects of a unit task
/// </summary>
public class AspectControlUnit
{
    private readonly List<IAspect> _aspects = new();
    private readonly List<AspectResult> _results = new();

    /// <summary>
    /// Register an aspect with the control unit
    /// </summary>
    public void RegisterAspect(IAspect aspect)
    {
        if (aspect == null)
            throw new ArgumentNullException(nameof(aspect));

        if (_aspects.Any(a => a.Id == aspect.Id))
            throw new InvalidOperationException($"Aspect with ID '{aspect.Id}' is already registered.");

        _aspects.Add(aspect);
    }

    /// <summary>
    /// Execute all registered aspects
    /// </summary>
    public async Task<List<AspectResult>> ExecuteAllAspectsAsync()
    {
        _results.Clear();

        foreach (var aspect in _aspects)
        {
            var result = await aspect.ExecuteAsync();
            _results.Add(result);
        }

        return _results;
    }

    /// <summary>
    /// Verify all aspects
    /// </summary>
    public async Task<bool> VerifyAllAspectsAsync()
    {
        foreach (var aspect in _aspects)
        {
            var verified = await aspect.VerifyAsync();
            if (!verified)
                return false;
        }

        return true;
    }

    /// <summary>
    /// Get all aspect results
    /// </summary>
    public IReadOnlyList<AspectResult> GetResults() => _results.AsReadOnly();

    /// <summary>
    /// Get registered aspects count
    /// </summary>
    public int GetAspectCount() => _aspects.Count;
}
