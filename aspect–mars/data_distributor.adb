-- Data Distribution and Algorithm Reporter
-- Distributes computation data and reports algorithm usage to terminal

with Ada.Text_IO;           use Ada.Text_IO;
with Ada.Float_Text_IO;     use Ada.Float_Text_IO;
with Ada.Calendar;          use Ada.Calendar;
with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;

procedure Data_Distributor is

   -- Type definitions
   type Algorithm_Type is (Compute_Difference, Compute_Sum, Compute_Product, Compute_Division);
   
   type Data_Package is record
      Value_A    : Float;
      Value_B    : Float;
      Algorithm  : Algorithm_Type;
      Timestamp  : Time;
   end record;
   
   type Data_Package_Array is array (Positive range <>) of Data_Package;
   
   -- Global configuration
   Distribution_Count : constant := 10;
   
   -- Function to get algorithm name as string
   function Algorithm_Name (Algo : Algorithm_Type) return String is
   begin
      case Algo is
         when Compute_Difference => return "COMPUTE_DIFFERENCE";
         when Compute_Sum        => return "COMPUTE_SUM";
         when Compute_Product    => return "COMPUTE_PRODUCT";
         when Compute_Division   => return "COMPUTE_DIVISION";
      end case;
   end Algorithm_Name;
   
   -- Procedure to execute the algorithm
   function Execute_Algorithm (Pkg : Data_Package) return Float is
      Result : Float;
   begin
      case Pkg.Algorithm is
         when Compute_Difference =>
            Result := Pkg.Value_A - Pkg.Value_B;
         when Compute_Sum =>
            Result := Pkg.Value_A + Pkg.Value_B;
         when Compute_Product =>
            Result := Pkg.Value_A * Pkg.Value_B;
         when Compute_Division =>
            if Pkg.Value_B /= 0.0 then
               Result := Pkg.Value_A / Pkg.Value_B;
            else
               Result := 0.0;
               Put_Line("   WARNING: Division by zero avoided");
            end if;
      end case;
      return Result;
   end Execute_Algorithm;
   
   -- Procedure to print separator line
   procedure Print_Separator is
   begin
      Put_Line("========================================================================");
   end Print_Separator;
   
   -- Procedure to print section header
   procedure Print_Header (Title : String) is
   begin
      Print_Separator;
      Put_Line(Title);
      Print_Separator;
   end Print_Header;
   
   -- Procedure to distribute and process a data package
   procedure Distribute_Package (Pkg : Data_Package; Index : Positive) is
      Result : Float;
   begin
      New_Line;
      Put_Line("DISTRIBUTION #" & Positive'Image(Index));
      Put_Line("---------------------------------------------");
      Put_Line("Algorithm: " & Algorithm_Name(Pkg.Algorithm));
      Put("Input Values: ");
      Put(Pkg.Value_A, Fore => 1, Aft => 2, Exp => 0);
      Put(" and ");
      Put(Pkg.Value_B, Fore => 1, Aft => 2, Exp => 0);
      New_Line;
      
      Result := Execute_Algorithm(Pkg);
      
      Put("Result: ");
      Put(Result, Fore => 1, Aft => 4, Exp => 0);
      New_Line;
      Put_Line("Status: ✓ Distributed and Executed");
   end Distribute_Package;
   
   -- Main data packages to distribute
   Data_Packages : Data_Package_Array(1 .. Distribution_Count) := (
      (100.0, 25.0, Compute_Difference, Clock),
      (50.0, 30.0, Compute_Difference, Clock),
      (200.0, 150.0, Compute_Difference, Clock),
      (10.5, 3.2, Compute_Difference, Clock),
      (7.5, 2.3, Compute_Sum, Clock),
      (15.0, 4.0, Compute_Product, Clock),
      (100.0, 5.0, Compute_Division, Clock),
      (88.0, 44.0, Compute_Difference, Clock),
      (12.5, 7.5, Compute_Sum, Clock),
      (6.0, 3.0, Compute_Product, Clock)
   );
   
   -- Statistics tracking
   Difference_Count : Natural := 0;
   Sum_Count        : Natural := 0;
   Product_Count    : Natural := 0;
   Division_Count   : Natural := 0;

begin
   -- Print header
   Print_Header("DATA DISTRIBUTOR - ALGORITHM REPORTING SYSTEM");
   Put_Line("System: Aspect Control Unit");
   Put_Line("Module: Data Distribution & Algorithm Dispatcher");
   New_Line;
   
   -- Distribute and process each package
   Print_Header("DATA DISTRIBUTION IN PROGRESS");
   
   for I in Data_Packages'Range loop
      Distribute_Package(Data_Packages(I), I);
      
      -- Count algorithm usage
      case Data_Packages(I).Algorithm is
         when Compute_Difference => Difference_Count := Difference_Count + 1;
         when Compute_Sum        => Sum_Count := Sum_Count + 1;
         when Compute_Product    => Product_Count := Product_Count + 1;
         when Compute_Division   => Division_Count := Division_Count + 1;
      end case;
   end loop;
   
   -- Print summary statistics
   New_Line;
   Print_Header("ALGORITHM USAGE STATISTICS");
   New_Line;
   Put_Line("Total Distributions: " & Natural'Image(Distribution_Count));
   New_Line;
   Put_Line("Algorithm Breakdown:");
   Put_Line("  - COMPUTE_DIFFERENCE: " & Natural'Image(Difference_Count) & 
            " distributions (" & 
            Natural'Image((Difference_Count * 100) / Distribution_Count) & "%)");
   Put_Line("  - COMPUTE_SUM:        " & Natural'Image(Sum_Count) & 
            " distributions (" & 
            Natural'Image((Sum_Count * 100) / Distribution_Count) & "%)");
   Put_Line("  - COMPUTE_PRODUCT:    " & Natural'Image(Product_Count) & 
            " distributions (" & 
            Natural'Image((Product_Count * 100) / Distribution_Count) & "%)");
   Put_Line("  - COMPUTE_DIVISION:   " & Natural'Image(Division_Count) & 
            " distributions (" & 
            Natural'Image((Division_Count * 100) / Distribution_Count) & "%)");
   New_Line;
   
   Print_Header("PRIMARY ALGORITHM USED");
   Put_Line("Algorithm: COMPUTE_DIFFERENCE");
   Put_Line("Usage: " & Natural'Image(Difference_Count) & " out of " & 
            Natural'Image(Distribution_Count) & " distributions");
   Put_Line("Description: Computes the numerical difference between two values");
   Put_Line("Formula: Result = Value_A - Value_B");
   New_Line;
   
   Print_Separator;
   Put_Line("✓ ALL DATA DISTRIBUTIONS COMPLETED SUCCESSFULLY");
   Print_Separator;
   
end Data_Distributor;
