using System;
using System.IO;
using System.Linq;
using Xunit;
using AspectControlUnit.Tools;

namespace AspectControlUnit.Tests
{
    public class FaxImagingToolTests
    {
        private readonly string _testDirectory = "TestFaxFiles";
        
        public FaxImagingToolTests()
        {
            if (!Directory.Exists(_testDirectory))
            {
                Directory.CreateDirectory(_testDirectory);
            }
        }

        [Fact]
        public void ProcessFax_WithValidFile_ReturnsSuccess()
        {
            // Arrange
            var tool = new FaxImagingTool();
            var testFile = CreateTestFaxFile("test_fax.dat");

            // Act
            var result = tool.ProcessFax(testFile);

            // Assert
            Assert.True(result.Success);
            Assert.NotEqual(Guid.Empty, result.FaxId);
            Assert.NotNull(result.OutputPath);
            Assert.True(File.Exists(result.OutputPath));
            
            // Cleanup
            File.Delete(testFile);
            if (File.Exists(result.OutputPath))
                File.Delete(result.OutputPath);
        }

        [Fact]
        public void ProcessFax_WithNonExistentFile_ReturnsFail()
        {
            // Arrange
            var tool = new FaxImagingTool();

            // Act
            var result = tool.ProcessFax("nonexistent_file.dat");

            // Assert
            Assert.False(result.Success);
            Assert.Contains("File not found", result.Message);
        }

        [Fact]
        public void ProcessBatch_WithMultipleFiles_ProcessesAll()
        {
            // Arrange
            var tool = new FaxImagingTool();
            var testFiles = new[]
            {
                CreateTestFaxFile("batch_fax1.dat"),
                CreateTestFaxFile("batch_fax2.dat"),
                CreateTestFaxFile("batch_fax3.dat")
            };

            // Act
            var result = tool.ProcessBatch(testFiles);

            // Assert
            Assert.Equal(3, result.TotalFiles);
            Assert.Equal(3, result.SuccessCount);
            Assert.Equal(0, result.FailureCount);
            Assert.True(result.TotalProcessingTimeMs > 0);

            // Cleanup
            foreach (var file in testFiles)
            {
                File.Delete(file);
            }
            foreach (var processResult in result.Results.Where(r => r.Success))
            {
                if (File.Exists(processResult.OutputPath))
                    File.Delete(processResult.OutputPath);
            }
        }

        [Fact]
        public void GetStatistics_AfterProcessing_ReturnsCorrectData()
        {
            // Arrange
            var tool = new FaxImagingTool();
            var testFile = CreateTestFaxFile("stats_test.dat");

            // Act
            tool.ProcessFax(testFile);
            var stats = tool.GetStatistics();

            // Assert
            Assert.Equal(1, stats.TotalProcessed);
            Assert.Equal(1, stats.CompletedCount);
            Assert.True(stats.TotalSizeBytes > 0);

            // Cleanup
            File.Delete(testFile);
        }

        [Fact]
        public void ClearHistory_RemovesProcessedImages()
        {
            // Arrange
            var tool = new FaxImagingTool();
            var testFile = CreateTestFaxFile("clear_test.dat");
            tool.ProcessFax(testFile);

            // Act
            tool.ClearHistory();
            var stats = tool.GetStatistics();

            // Assert
            Assert.Equal(0, stats.TotalProcessed);

            // Cleanup
            File.Delete(testFile);
        }

        private string CreateTestFaxFile(string filename)
        {
            var path = Path.Combine(_testDirectory, filename);
            var testData = new byte[1024];
            new Random().NextBytes(testData);
            File.WriteAllBytes(path, testData);
            return path;
        }
    }
}
