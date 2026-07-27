using Xunit;
using AspectControlUnit.Aspects;

namespace AspectControlUnit.Tests;

/// <summary>
/// Unit tests for ComputeDifferenceAspect
/// </summary>
public class ComputeDifferenceAspectTests
{
    [Fact]
    public async Task ExecuteAsync_ShouldComputeDifference()
    {
        // Arrange
        var aspect = new ComputeDifferenceAspect("diff-1", "Difference Test", 10.5, 3.2);

        // Act
        var result = await aspect.ExecuteAsync();

        // Assert
        Assert.True(result.Success);
        Assert.Equal("diff-1", result.AspectId);
        Assert.NotNull(result.Data);
    }

    [Fact]
    public async Task ExecuteAsync_WithNegativeResult_ShouldSucceed()
    {
        // Arrange
        var aspect = new ComputeDifferenceAspect("diff-2", "Negative Difference", 5, 10);

        // Act
        var result = await aspect.ExecuteAsync();

        // Assert
        Assert.True(result.Success);
        Assert.Contains("-5", result.Message);
    }

    [Fact]
    public async Task VerifyAsync_AfterExecution_ShouldReturnTrue()
    {
        // Arrange
        var aspect = new ComputeDifferenceAspect("diff-3", "Verify Test", 100, 25);

        // Act
        await aspect.ExecuteAsync();
        var verified = await aspect.VerifyAsync();

        // Assert
        Assert.True(verified);
    }

    [Fact]
    public async Task VerifyAsync_BeforeExecution_ShouldReturnFalse()
    {
        // Arrange
        var aspect = new ComputeDifferenceAspect("diff-4", "No Execution", 50, 20);

        // Act
        var verified = await aspect.VerifyAsync();

        // Assert
        Assert.False(verified);
    }

    [Theory]
    [InlineData(10, 5, 5)]
    [InlineData(100, 50, 50)]
    [InlineData(0, 0, 0)]
    [InlineData(-10, -5, -5)]
    [InlineData(7.5, 2.3, 5.2)]
    public async Task ExecuteAsync_WithVariousValues_ShouldComputeCorrectly(
        double valueA, double valueB, double expectedDifference)
    {
        // Arrange
        var aspect = new ComputeDifferenceAspect("diff-theory", "Theory Test", valueA, valueB);

        // Act
        var result = await aspect.ExecuteAsync();
        await aspect.VerifyAsync();

        // Assert
        Assert.True(result.Success);
        var difference = result.Message.Split(':')[1].Trim();
        Assert.Equal(expectedDifference.ToString(), difference);
    }
}
