using Xunit;
using AspectControlUnit.Core;
using AspectControlUnit.Aspects;

namespace AspectControlUnit.Tests;

/// <summary>
/// Unit tests for AspectControlUnit
/// </summary>
public class AspectControlUnitTests
{
    [Fact]
    public void RegisterAspect_ShouldAddAspect()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect = new ComputeDifferenceAspect("test-1", "Test Aspect", 10, 5);

        // Act
        controlUnit.RegisterAspect(aspect);

        // Assert
        Assert.Equal(1, controlUnit.GetAspectCount());
    }

    [Fact]
    public void RegisterAspect_WithNullAspect_ShouldThrowArgumentNullException()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();

        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => controlUnit.RegisterAspect(null!));
    }

    [Fact]
    public void RegisterAspect_WithDuplicateId_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect1 = new ComputeDifferenceAspect("test-1", "Test Aspect 1", 10, 5);
        var aspect2 = new ComputeDifferenceAspect("test-1", "Test Aspect 2", 20, 10);

        // Act
        controlUnit.RegisterAspect(aspect1);

        // Assert
        Assert.Throws<InvalidOperationException>(() => controlUnit.RegisterAspect(aspect2));
    }

    [Fact]
    public async Task ExecuteAllAspectsAsync_ShouldExecuteAllAspects()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect1 = new ComputeDifferenceAspect("test-1", "Aspect 1", 10, 5);
        var aspect2 = new ComputeDifferenceAspect("test-2", "Aspect 2", 20, 8);

        controlUnit.RegisterAspect(aspect1);
        controlUnit.RegisterAspect(aspect2);

        // Act
        var results = await controlUnit.ExecuteAllAspectsAsync();

        // Assert
        Assert.Equal(2, results.Count);
        Assert.All(results, result => Assert.True(result.Success));
    }

    [Fact]
    public async Task VerifyAllAspectsAsync_AfterExecution_ShouldReturnTrue()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect = new ComputeDifferenceAspect("test-1", "Test Aspect", 10, 5);

        controlUnit.RegisterAspect(aspect);
        await controlUnit.ExecuteAllAspectsAsync();

        // Act
        var verified = await controlUnit.VerifyAllAspectsAsync();

        // Assert
        Assert.True(verified);
    }

    [Fact]
    public async Task VerifyAllAspectsAsync_BeforeExecution_ShouldReturnFalse()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect = new ComputeDifferenceAspect("test-1", "Test Aspect", 10, 5);

        controlUnit.RegisterAspect(aspect);

        // Act
        var verified = await controlUnit.VerifyAllAspectsAsync();

        // Assert
        Assert.False(verified);
    }
}
