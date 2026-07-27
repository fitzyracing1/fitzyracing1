using System;
using System.IO;
using System.Linq;
using AspectControlUnit.Tools;

namespace FaxImagingRunner
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("╔══════════════════════════════════════════╗");
            Console.WriteLine("║   ABRUPT FAX IMAGING TOOL v1.0           ║");
            Console.WriteLine("║   Rapid Fax Processing System            ║");
            Console.WriteLine("╚══════════════════════════════════════════╝");
            Console.WriteLine();

            var tool = new FaxImagingTool();

            if (args.Length == 0)
            {
                ShowMenu(tool);
            }
            else
            {
                ProcessCommandLineArgs(tool, args);
            }
        }

        static void ShowMenu(FaxImagingTool tool)
        {
            while (true)
            {
                Console.WriteLine("\nSelect an option:");
                Console.WriteLine("1. Process single fax file");
                Console.WriteLine("2. Process batch of fax files");
                Console.WriteLine("3. View statistics");
                Console.WriteLine("4. Clear history");
                Console.WriteLine("5. Create demo fax files");
                Console.WriteLine("6. Exit");
                Console.Write("\nChoice: ");

                var choice = Console.ReadLine();

                switch (choice)
                {
                    case "1":
                        ProcessSingleFile(tool);
                        break;
                    case "2":
                        ProcessBatchFiles(tool);
                        break;
                    case "3":
                        ShowStatistics(tool);
                        break;
                    case "4":
                        tool.ClearHistory();
                        Console.WriteLine("✓ History cleared");
                        break;
                    case "5":
                        CreateDemoFiles();
                        break;
                    case "6":
                        return;
                    default:
                        Console.WriteLine("Invalid choice");
                        break;
                }
            }
        }

        static void ProcessSingleFile(FaxImagingTool tool)
        {
            Console.Write("Enter fax file path: ");
            var path = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(path))
            {
                Console.WriteLine("✗ Invalid path");
                return;
            }

            Console.WriteLine("\n⚡ Processing abruptly...");
            var result = tool.ProcessFax(path);

            if (result.Success)
            {
                Console.WriteLine($"✓ SUCCESS");
                Console.WriteLine($"  Fax ID: {result.FaxId}");
                Console.WriteLine($"  Output: {result.OutputPath}");
                Console.WriteLine($"  Time: {result.ProcessingTimeMs:F2}ms");
            }
            else
            {
                Console.WriteLine($"✗ FAILED: {result.Message}");
            }
        }

        static void ProcessBatchFiles(FaxImagingTool tool)
        {
            Console.Write("Enter directory path containing fax files: ");
            var directory = Console.ReadLine();

            if (!Directory.Exists(directory))
            {
                Console.WriteLine("✗ Directory not found");
                return;
            }

            var files = Directory.GetFiles(directory, "*.dat")
                .Concat(Directory.GetFiles(directory, "*.tif"))
                .Concat(Directory.GetFiles(directory, "*.tiff"))
                .Concat(Directory.GetFiles(directory, "*.jpg"))
                .ToArray();

            if (files.Length == 0)
            {
                Console.WriteLine("✗ No fax files found");
                return;
            }

            Console.WriteLine($"\n⚡ Processing {files.Length} files abruptly...");
            var result = tool.ProcessBatch(files);

            Console.WriteLine($"\n✓ BATCH COMPLETE");
            Console.WriteLine($"  Total Files: {result.TotalFiles}");
            Console.WriteLine($"  Success: {result.SuccessCount}");
            Console.WriteLine($"  Failed: {result.FailureCount}");
            Console.WriteLine($"  Total Time: {result.TotalProcessingTimeMs:F2}ms");
            Console.WriteLine($"  Avg Time/File: {result.TotalProcessingTimeMs / result.TotalFiles:F2}ms");
        }

        static void ShowStatistics(FaxImagingTool tool)
        {
            var stats = tool.GetStatistics();

            Console.WriteLine("\n╔══════════════════════════════════════════╗");
            Console.WriteLine("║         PROCESSING STATISTICS            ║");
            Console.WriteLine("╚══════════════════════════════════════════╝");
            Console.WriteLine($"Total Processed:   {stats.TotalProcessed}");
            Console.WriteLine($"Completed:         {stats.CompletedCount}");
            Console.WriteLine($"Failed:            {stats.FailedCount}");
            Console.WriteLine($"Total Size:        {FormatBytes(stats.TotalSizeBytes)}");
            Console.WriteLine($"Average File Size: {FormatBytes((long)stats.AverageFileSizeBytes)}");
        }

        static void CreateDemoFiles()
        {
            var demoDir = "DemoFaxFiles";
            if (!Directory.Exists(demoDir))
            {
                Directory.CreateDirectory(demoDir);
            }

            var random = new Random();
            for (int i = 1; i <= 5; i++)
            {
                var filename = Path.Combine(demoDir, $"demo_fax_{i}.dat");
                var data = new byte[1024 * (i + 1)]; // Varying sizes
                random.NextBytes(data);
                File.WriteAllBytes(filename, data);
            }

            Console.WriteLine($"✓ Created 5 demo fax files in '{demoDir}' directory");
        }

        static void ProcessCommandLineArgs(FaxImagingTool tool, string[] args)
        {
            if (args.Length == 1)
            {
                var result = tool.ProcessFax(args[0]);
                Console.WriteLine(result.Success ? 
                    $"✓ Processed: {result.OutputPath}" : 
                    $"✗ Failed: {result.Message}");
            }
            else
            {
                var result = tool.ProcessBatch(args);
                Console.WriteLine($"✓ Processed {result.SuccessCount}/{result.TotalFiles} files");
            }
        }

        static string FormatBytes(long bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB" };
            double len = bytes;
            int order = 0;
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len /= 1024;
            }
            return $"{len:0.##} {sizes[order]}";
        }
    }
}
