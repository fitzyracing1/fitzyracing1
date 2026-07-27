#!/usr/bin/env python3
"""
Interactive Quantum AI System Demo
Allows users to interactively create, evolve, and manage AIs
"""

from quantum_ai_controller import QuantumAIController
from quantum_ai_core import QuantumAICore
import json


def print_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("QUANTUM AI SYSTEM - Interactive Demo")
    print("="*60)
    print("\n1. Initialize AI Ecosystem")
    print("2. Spawn Task-Specific AI")
    print("3. Create AI Network")
    print("4. Evolve Existing AI")
    print("5. View System Status")
    print("6. List All AIs")
    print("7. Cloning an AI")
    print("8. Save System State")
    print("9. Exit")
    print("\n" + "-"*60)


def initialize_ecosystem(controller: QuantumAIController):
    """Initialize the AI ecosystem"""
    num_layers = 2
    print(f"\nInitializing ecosystem with {num_layers} layers...")
    ecosystem = controller.initialize_ecosystem(num_layers=num_layers)
    print(f"✓ Created {ecosystem['total_ais']} AIs across {len(ecosystem['layers'])} layers")
    for layer in ecosystem['layers']:
        print(f"  - Layer {layer['layer']}: {layer['count']} AIs")


def spawn_task_ai(controller: QuantumAIController):
    """Spawn task-specific AI"""
    print("\nTask-Specific AI Creation")
    print("-" * 40)
    task = input("Enter task description (e.g., 'Classify images'): ").strip()
    
    if task:
        ai = controller.spawn_ai_for_task(task)
        print(f"\n✓ Created: {ai['name']}")
        print(f"  ID: {ai['id']}")
        print(f"  Type: {ai['type']}")
        print(f"  Task: {ai['task_specific']['task']}")
    else:
        print("No task provided.")


def create_network(controller: QuantumAIController):
    """Create collaborative AI network"""
    print("\nCreate Collaborative Network")
    print("-" * 40)
    print("1. Mesh (fully connected)")
    print("2. Star (central hub)")
    print("3. Chain (sequential)")
    
    choice = input("\nSelect topology (1-3): ").strip()
    topology_map = {"1": "mesh", "2": "star", "3": "chain"}
    topology = topology_map.get(choice, "mesh")
    
    print(f"\nCreating {topology} network...")
    network = controller.create_collaborative_network(topology=topology)
    print(f"✓ Created {topology} network")
    print(f"  AIs: {len(network['network_ais'])}")
    print(f"  Connections: {network['connections']}")


def evolve_ai(controller: QuantumAIController):
    """Evolve an AI"""
    print("\nEvolve AI")
    print("-" * 40)
    
    status = controller.get_system_status()
    ais = status['all_ais']
    
    if not ais:
        print("No AIs to evolve. Create some first!")
        return
    
    print("\nAvailable AIs:")
    for i, ai in enumerate(ais[:10]):  # Show first 10
        print(f"{i+1}. {ai['name']} (Type: {ai['type']})")
    
    choice = input("\nSelect AI number: ").strip()
    try:
        ai_idx = int(choice) - 1
        if 0 <= ai_idx < len(ais):
            ai = ais[ai_idx]
            method = input("Evolution method (mutate/crossover): ").strip().lower()
            
            if method in ["mutate", "crossover"]:
                evolved = controller.evolve_ai(ai['id'], method=method)
                print(f"\n✓ Created evolved AI: {evolved['name']}")
                print(f"  ID: {evolved['id']}")
            else:
                print("Invalid method.")
    except ValueError:
        print("Invalid selection.")


def view_status(controller: QuantumAIController):
    """View system status"""
    print("\nSystem Status")
    print("-" * 40)
    status = controller.get_system_status()
    
    print(f"System: {status['system_name']}")
    print(f"Meta-AI: {status['meta_ai_name']}")
    
    stats = status['statistics']
    print(f"\nStatistics:")
    print(f"  Total AIs Generated: {stats['total_ais_generated']}")
    print(f"  Total Qubits: {stats['total_qubits']}")
    print(f"  Entangled Pairs: {stats['entangled_pairs']}")
    print(f"\nAIs by Type:")
    for ai_type, count in stats['ais_by_type'].items():
        print(f"  - {ai_type}: {count}")


def list_all_ais(controller: QuantumAIController):
    """List all generated AIs"""
    print("\nAll Generated AIs")
    print("-" * 60)
    
    status = controller.get_system_status()
    ais = status['all_ais']
    
    if not ais:
        print("No AIs generated yet.")
        return
    
    print(f"{'Name':<30} {'Type':<20} {'Status':<10}")
    print("-" * 60)
    for ai in ais:
        name = ai['name'][:28]
        ai_type = ai['type'][:18]
        status = ai['status'][:8]
        print(f"{name:<30} {ai_type:<20} {status:<10}")
    
    print(f"\nTotal: {len(ais)} AIs")


def clone_ai(controller: QuantumAIController):
    """Clone an AI"""
    print("\nClone AI")
    print("-" * 40)
    
    status = controller.get_system_status()
    ais = status['all_ais']
    
    if not ais:
        print("No AIs to clone.")
        return
    
    print("Select AI to clone:")
    for i, ai in enumerate(ais[:10]):
        print(f"{i+1}. {ai['name']}")
    
    try:
        choice = int(input("\nSelect number: ").strip()) - 1
        if 0 <= choice < len(ais):
            source_ai = ais[choice]
            new_name = input("New AI name (optional): ").strip()
            
            cloned = controller.meta_ai.quantum_core.clone_ai(
                source_ai['id'],
                new_name=new_name if new_name else None
            )
            print(f"\n✓ Cloned: {cloned['name']}")
            print(f"  ID: {cloned['id']}")
    except ValueError:
        print("Invalid selection.")


def save_state(controller: QuantumAIController):
    """Save system state"""
    print("\nSave System State")
    print("-" * 40)
    filename = input("Filename (default: quantum_ai_state.json): ").strip()
    if not filename:
        filename = "../data/quantum_ai_state.json"
    
    controller.save_system_state(filename)
    print(f"✓ State saved to {filename}")


def main():
    """Main interactive loop"""
    print("\n" + "="*60)
    print("QUANTUM AI SYSTEM")
    print("AI Building AI - Interactive Demo")
    print("="*60)
    
    # Initialize controller
    controller = QuantumAIController(system_name="Interactive-QuantumAI")
    
    while True:
        print_menu()
        choice = input("Select option (1-9): ").strip()
        
        try:
            if choice == "1":
                initialize_ecosystem(controller)
            elif choice == "2":
                spawn_task_ai(controller)
            elif choice == "3":
                create_network(controller)
            elif choice == "4":
                evolve_ai(controller)
            elif choice == "5":
                view_status(controller)
            elif choice == "6":
                list_all_ais(controller)
            elif choice == "7":
                clone_ai(controller)
            elif choice == "8":
                save_state(controller)
            elif choice == "9":
                print("\n✓ Exiting Quantum AI System")
                print("Thank you for using the system!")
                break
            else:
                print("Invalid option. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
