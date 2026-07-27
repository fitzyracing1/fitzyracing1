"""
JARVIS - Autonomous Technical Bot for Mechanical Parts Creation
Main entry point and orchestrator
"""
import os
import sys
import time
from datetime import datetime

# Add bot_parts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot_parts'))

from nlp import NLPTask
from ml import MLTask
from file_manager import FileManager


class MechanicsJarvis:
    """
    JARVIS - Autonomous bot that generates mechanical parts based on predictions
    and continuously creates files from its own cycles
    """
    
    def __init__(self, autonomous_mode=True):
        """
        Initialize JARVIS
        
        Args:
            autonomous_mode: If True, JARVIS generates parts autonomously
        """
        self.nlp_task = NLPTask()
        self.ml_task = MLTask()
        self.file_manager = FileManager(base_path='data')
        self.autonomous_mode = autonomous_mode
        self.cycle_count = 0
        self.is_running = False
        
        print(f"{'='*60}")
        print(f"JARVIS - Mechanical Parts Creation Bot")
        print(f"{'='*60}")
        print(f"Autonomous Mode: {autonomous_mode}")
        print(f"Workspace: {os.path.abspath('data')}")
        print(f"{'='*60}\n")
    
    def autonomous_generation_cycle(self, cycle_delay=2):
        """
        Run an autonomous generation cycle - JARVIS creates parts without user input
        
        Args:
            cycle_delay: Delay between cycles in seconds
        """
        try:
            self.cycle_count += 1
            
            print(f"\n[CYCLE {self.cycle_count}] Starting autonomous generation cycle...")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Generate parts based on predictions
            num_parts = 3  # Generate 3 parts per cycle
            print(f"Generating {num_parts} new mechanical parts...")
            
            predictions = self.ml_task.predict_batch(count=num_parts)
            
            # Save generated parts to files
            filepaths = self.file_manager.save_batch(predictions)
            
            # Display generated parts
            for i, (part, filepath) in enumerate(zip(predictions, filepaths), 1):
                print(f"\n  Part {i}:")
                print(f"    Name: {part['name']}")
                print(f"    Category: {part['category']}")
                print(f"    Type: {part['type']}")
                print(f"    Material: {part['material']}")
                print(f"    Dimensions: {part['dimensions']['diameter']}mm ⌀ × {part['dimensions']['width']}mm W")
                print(f"    File: {os.path.basename(filepath)}")
                print(f"    Confidence: {part['confidence_score']:.2%}")
            
            # Generate and save metadata
            stats = self.ml_task.get_part_statistics()
            metadata = {
                'cycle': self.cycle_count,
                'timestamp': datetime.now().isoformat(),
                'parts_generated': len(predictions),
                'statistics': stats
            }
            
            metadata_file = self.file_manager.save_metadata(metadata)
            print(f"\nMetadata saved: {os.path.basename(metadata_file)}")
            
            print(f"\n[CYCLE {self.cycle_count}] Cycle completed successfully!")
            print(f"Total parts generated so far: {self.ml_task.generation_count}")
            
            # Wait for next cycle
            if self.is_running:
                print(f"Waiting {cycle_delay}s before next cycle...\n")
                time.sleep(cycle_delay)
        
        except Exception as e:
            print(f"Error during cycle {self.cycle_count}: {str(e)}")
            self.file_manager.session_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'cycle_failed',
                'cycle': self.cycle_count,
                'error': str(e)
            })
    
    def interactive_mode(self):
        """Run JARVIS in interactive mode with user input"""
        print("\n[INTERACTIVE MODE]")
        print("Commands:")
        print("  'generate [n]' - Generate n mechanical parts")
        print("  'status'       - Show generation statistics")
        print("  'list'         - List all generated parts")
        print("  'auto [n]'     - Start autonomous cycles (n seconds delay)")
        print("  'stop'         - Stop autonomous generation")
        print("  'exit'         - Exit JARVIS")
        print("")
        
        while True:
            try:
                user_input = input("JARVIS> ").strip().lower()
                
                if not user_input:
                    continue
                
                if user_input == 'exit':
                    print("JARVIS shutting down...")
                    break
                
                elif user_input == 'stop':
                    self.is_running = False
                    print("Autonomous generation stopped.")
                
                elif user_input.startswith('generate'):
                    parts_count = 1
                    if len(user_input.split()) > 1:
                        try:
                            parts_count = int(user_input.split()[1])
                        except ValueError:
                            parts_count = 1
                    
                    print(f"\nGenerating {parts_count} part(s)...")
                    predictions = self.ml_task.predict_batch(count=parts_count)
                    filepaths = self.file_manager.save_batch(predictions)
                    
                    for part, filepath in zip(predictions, filepaths):
                        print(f"  ✓ {part['name']} → {os.path.basename(filepath)}")
                
                elif user_input.startswith('auto'):
                    delay = 2
                    if len(user_input.split()) > 1:
                        try:
                            delay = int(user_input.split()[1])
                        except ValueError:
                            delay = 2
                    
                    print(f"\nStarting autonomous generation (delay: {delay}s)...")
                    print("Press Ctrl+C to stop.\n")
                    
                    self.is_running = True
                    try:
                        while self.is_running:
                            self.autonomous_generation_cycle(cycle_delay=delay)
                    except KeyboardInterrupt:
                        print("\n\nAutonomous generation stopped by user.")
                        self.is_running = False
                
                elif user_input == 'status':
                    stats = self.ml_task.get_part_statistics()
                    print("\n[GENERATION STATISTICS]")
                    print(f"Total parts generated: {self.ml_task.generation_count}")
                    if stats:
                        print(f"Types: {stats.get('types_distribution', {})}")
                        print(f"Materials: {stats.get('materials_distribution', {})}")
                        print(f"Average confidence: {stats.get('average_confidence', 'N/A'):.2%}")
                
                elif user_input == 'list':
                    parts = self.file_manager.list_generated_parts()
                    print(f"\n[GENERATED PARTS] ({len(parts)} files)")
                    for part_file in sorted(parts)[-10:]:  # Show last 10
                        print(f"  • {part_file}")
                    if len(parts) > 10:
                        print(f"  ... and {len(parts) - 10} more")
                
                else:
                    print(f"Unknown command: {user_input}")
            
            except KeyboardInterrupt:
                print("\n\nJARVIS shutting down...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def run_autonomous(self, num_cycles=5, cycle_delay=2):
        """
        Run JARVIS in fully autonomous mode for a set number of cycles
        
        Args:
            num_cycles: Number of generation cycles to run
            cycle_delay: Delay between cycles in seconds
        """
        print(f"\n[AUTONOMOUS MODE] Running {num_cycles} cycles...\n")
        self.is_running = True
        
        try:
            for _ in range(num_cycles):
                if self.is_running:
                    self.autonomous_generation_cycle(cycle_delay=cycle_delay)
        except KeyboardInterrupt:
            print("\n\nAutonomous generation interrupted by user.")
        finally:
            self.is_running = False
            self._save_final_report()
    
    def _save_final_report(self):
        """Save final session report"""
        session_log = self.file_manager.save_session_log()
        summary = self.file_manager.get_session_summary()
        
        print(f"\n{'='*60}")
        print(f"SESSION REPORT")
        print(f"{'='*60}")
        print(f"Total cycles completed: {self.cycle_count}")
        print(f"Total parts generated: {self.ml_task.generation_count}")
        print(f"Files created: {summary['files_created']}")
        print(f"Session log: {os.path.basename(session_log)}")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS - Mechanical Parts Creation Bot')
    parser.add_argument('--mode', choices=['interactive', 'autonomous'], default='interactive',
                       help='Operation mode (default: interactive)')
    parser.add_argument('--cycles', type=int, default=5,
                       help='Number of cycles for autonomous mode (default: 5)')
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay between cycles in seconds (default: 2)')
    
    args = parser.parse_args()
    
    # Initialize JARVIS
    jarvis = MechanicsJarvis(autonomous_mode=(args.mode == 'autonomous'))
    
    try:
        if args.mode == 'autonomous':
            jarvis.run_autonomous(num_cycles=args.cycles, cycle_delay=args.delay)
        else:
            jarvis.interactive_mode()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        jarvis._save_final_report()


if __name__ == '__main__':
    main()
