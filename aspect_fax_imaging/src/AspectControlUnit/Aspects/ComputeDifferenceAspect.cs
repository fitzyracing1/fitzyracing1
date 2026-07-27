using AspectControlUnit.Interfaces;
using AspectControlUnit.Models;

namespace AspectControlUnit.Aspects;

/// <summary>
/// Aspect that computes differences between values
/// </summary>
public class ComputeDifferenceAspect : IAspect
{
    private readonly double _valueA;
    private readonly double _valueB;
    private ComputeDifference? _lastComputation;

    public string Id { get; }
    public string Name { get; }

    public ComputeDifferenceAspect(string id, string name, double valueA, double valueB)
    {
        Id = id;
        Name = name;
        _valueA = valueA;
        _valueB = valueB;
    }

    public Task<AspectResult> ExecuteAsync()
    {
        try
        {
            var difference = _valueA - _valueB;

            _lastComputation = new ComputeDifference
            {
                ValueA = _valueA,
                ValueB = _valueB,
                Difference = difference,
                DifferenceType = "Numeric",
                ComputedAt = DateTime.UtcNow
            };

            return Task.FromResult(new AspectResult
            {
                AspectId = Id,
                Success = true,
                Message = $"Computed difference: {difference}",
                Data = _lastComputation
            });
        }
        catch (Exception ex)
        {
            return Task.FromResult(new AspectResult
            {
                AspectId = Id,
                Success = false,
                Message = $"Error computing difference: {ex.Message}"
            });
        }
    }

    public Task<bool> VerifyAsync()
    {
        // Verify the computation was performed
        if (_lastComputation == null)
            return Task.FromResult(false);

        // Verify the difference calculation is correct
        var expectedDifference = _valueA - _valueB;
        var actualDifference = (double)(_lastComputation.Difference ?? 0);

        return Task.FromResult(Math.Abs(expectedDifference - actualDifference) < 0.0001);
    }
}
