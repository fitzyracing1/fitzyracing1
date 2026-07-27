using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace AspectControlUnit.Tools
{
    /// <summary>
    /// Abrupt Fax Imaging Tool - Provides rapid fax image processing and conversion capabilities
    /// </summary>
    public class FaxImagingTool
    {
        private readonly string _outputDirectory;
        private readonly List<FaxImage> _processedImages;

        public FaxImagingTool(string outputDirectory = "FaxOutput")
        {
            _outputDirectory = outputDirectory;
            _processedImages = new List<FaxImage>();
            
            if (!Directory.Exists(_outputDirectory))
            {
                Directory.CreateDirectory(_outputDirectory);
            }
        }

        /// <summary>
        /// Abruptly processes a fax image file
        /// </summary>
        public FaxProcessResult ProcessFax(string filePath)
        {
            if (!File.Exists(filePath))
            {
                return new FaxProcessResult 
                { 
                    Success = false, 
                    Message = "File not found",
                    ProcessingTimeMs = 0
                };
            }

            var startTime = DateTime.Now;
            
            try
            {
                var fileInfo = new FileInfo(filePath);
                var faxImage = new FaxImage
                {
                    Id = Guid.NewGuid(),
                    OriginalPath = filePath,
                    FileName = fileInfo.Name,
                    FileSizeBytes = fileInfo.Length,
                    ProcessedDate = DateTime.Now,
                    Status = FaxStatus.Processing
                };

                // Simulate abrupt image processing
                byte[] imageData = File.ReadAllBytes(filePath);
                
                // Apply rapid compression/conversion
                var processedData = ApplyAbruptProcessing(imageData);
                
                // Save processed image
                string outputPath = Path.Combine(_outputDirectory, 
                    $"processed_{faxImage.Id}_{fileInfo.Name}");
                File.WriteAllBytes(outputPath, processedData);
                
                faxImage.ProcessedPath = outputPath;
                faxImage.Status = FaxStatus.Completed;
                
                _processedImages.Add(faxImage);

                var processingTime = (DateTime.Now - startTime).TotalMilliseconds;

                return new FaxProcessResult
                {
                    Success = true,
                    Message = "Fax processed abruptly",
                    FaxId = faxImage.Id,
                    OutputPath = outputPath,
                    ProcessingTimeMs = processingTime
                };
            }
            catch (Exception ex)
            {
                var processingTime = (DateTime.Now - startTime).TotalMilliseconds;
                return new FaxProcessResult
                {
                    Success = false,
                    Message = $"Processing failed: {ex.Message}",
                    ProcessingTimeMs = processingTime
                };
            }
        }

        /// <summary>
        /// Batch process multiple fax images abruptly
        /// </summary>
        public BatchFaxResult ProcessBatch(string[] filePaths)
        {
            var results = new List<FaxProcessResult>();
            var startTime = DateTime.Now;

            foreach (var filePath in filePaths)
            {
                results.Add(ProcessFax(filePath));
            }

            return new BatchFaxResult
            {
                TotalFiles = filePaths.Length,
                SuccessCount = results.Count(r => r.Success),
                FailureCount = results.Count(r => !r.Success),
                TotalProcessingTimeMs = (DateTime.Now - startTime).TotalMilliseconds,
                Results = results
            };
        }

        /// <summary>
        /// Applies abrupt image processing transformations
        /// </summary>
        private byte[] ApplyAbruptProcessing(byte[] imageData)
        {
            // Simulate rapid processing: contrast enhancement, noise reduction, compression
            var processed = new byte[imageData.Length];
            
            for (int i = 0; i < imageData.Length; i++)
            {
                // Simple contrast adjustment
                processed[i] = (byte)Math.Min(255, imageData[i] * 1.2);
            }

            return processed;
        }

        /// <summary>
        /// Gets processing statistics
        /// </summary>
        public FaxStatistics GetStatistics()
        {
            return new FaxStatistics
            {
                TotalProcessed = _processedImages.Count,
                CompletedCount = _processedImages.Count(f => f.Status == FaxStatus.Completed),
                FailedCount = _processedImages.Count(f => f.Status == FaxStatus.Failed),
                TotalSizeBytes = _processedImages.Sum(f => f.FileSizeBytes),
                AverageFileSizeBytes = _processedImages.Any() ? 
                    _processedImages.Average(f => f.FileSizeBytes) : 0
            };
        }

        /// <summary>
        /// Clears processed fax history
        /// </summary>
        public void ClearHistory()
        {
            _processedImages.Clear();
        }
    }

    public class FaxImage
    {
        public Guid Id { get; set; }
        public string OriginalPath { get; set; }
        public string ProcessedPath { get; set; }
        public string FileName { get; set; }
        public long FileSizeBytes { get; set; }
        public DateTime ProcessedDate { get; set; }
        public FaxStatus Status { get; set; }
    }

    public class FaxProcessResult
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public Guid FaxId { get; set; }
        public string OutputPath { get; set; }
        public double ProcessingTimeMs { get; set; }
    }

    public class BatchFaxResult
    {
        public int TotalFiles { get; set; }
        public int SuccessCount { get; set; }
        public int FailureCount { get; set; }
        public double TotalProcessingTimeMs { get; set; }
        public List<FaxProcessResult> Results { get; set; }
    }

    public class FaxStatistics
    {
        public int TotalProcessed { get; set; }
        public int CompletedCount { get; set; }
        public int FailedCount { get; set; }
        public long TotalSizeBytes { get; set; }
        public double AverageFileSizeBytes { get; set; }
    }

    public enum FaxStatus
    {
        Pending,
        Processing,
        Completed,
        Failed
    }
}
