using Xunit;
using AspectControlUnit.Core;
using AspectControlUnit.Aspects;
using AspectControlUnit.Interfaces;

namespace AspectControlUnit.Tests;

/// <summary>
/// System-level integration tests
/// </summary>
public class SystemFunctionTests
{
    [Fact]
    public async Task FullSystemTest_WithMultipleAspects_ShouldExecuteAndVerify()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();

        var aspect1 = new ComputeDifferenceAspect("sys-1", "System Test 1", 100, 25);
        var aspect2 = new ComputeDifferenceAspect("sys-2", "System Test 2", 50, 30);
        var aspect3 = new ComputeDifferenceAspect("sys-3", "System Test 3", 200, 150);

        controlUnit.RegisterAspect(aspect1);
        controlUnit.RegisterAspect(aspect2);
        controlUnit.RegisterAspect(aspect3);

        // Act
        var results = await controlUnit.ExecuteAllAspectsAsync();
        var verified = await controlUnit.VerifyAllAspectsAsync();

        // Assert
        Assert.Equal(3, results.Count);
        Assert.All(results, result => Assert.True(result.Success));
        Assert.True(verified);
    }

    [Fact]
    public async Task SystemTest_SequentialExecution_ShouldMaintainState()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect = new ComputeDifferenceAspect("seq-1", "Sequential Test", 1000, 250);

        controlUnit.RegisterAspect(aspect);

        // Act - First execution
        var results1 = await controlUnit.ExecuteAllAspectsAsync();
        var verified1 = await controlUnit.VerifyAllAspectsAsync();

        // Act - Second execution (should update results)
        var results2 = await controlUnit.ExecuteAllAspectsAsync();
        var verified2 = await controlUnit.VerifyAllAspectsAsync();

        // Assert
        Assert.Single(results1);
        Assert.Single(results2);
        Assert.True(verified1);
        Assert.True(verified2);
    }

    [Fact]
    public async Task SystemTest_EmptyControlUnit_ShouldHandleGracefully()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();

        // Act
        var results = await controlUnit.ExecuteAllAspectsAsync();
        var verified = await controlUnit.VerifyAllAspectsAsync();

        // Assert
        Assert.Empty(results);
        Assert.True(verified); // Empty set should verify successfully
    }

    [Fact]
    public async Task SystemTest_GetResults_ShouldReturnReadOnlyCollection()
    {
        // Arrange
        var controlUnit = new Core.AspectControlUnit();
        var aspect = new ComputeDifferenceAspect("ro-1", "ReadOnly Test", 75, 25);

        controlUnit.RegisterAspect(aspect);
        await controlUnit.ExecuteAllAspectsAsync();

        // Act
        var results = controlUnit.GetResults();

        // Assert
        Assert.NotNull(results);
        Assert.Single(results);
        Assert.IsAssignableFrom<IReadOnlyList<AspectResult>>(results);
    }
}
