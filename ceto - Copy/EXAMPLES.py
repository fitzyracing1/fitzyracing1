"""
Example Usage Patterns for Quantum AI System
Demonstrates common workflows and use cases
"""

from src.quantum_ai_controller import QuantumAIController
from src.quantum_ai_core import QuantumAICore


# ==============================================================================
# EXAMPLE 1: Basic AI Generation
# ==============================================================================

def example_basic_generation():
    """Generate a single AI instance"""
    print("\n=== EXAMPLE 1: Basic AI Generation ===\n")
    
    # Create core system
    core = QuantumAICore(name="BasicCore", num_qubits=8)
    
    # Generate different types of AIs
    classifier = core.generate_ai("text_classifier")
    generator = core.generate_ai("data_generator")
    analyzer = core.generate_ai("analyzer")
    learner = core.generate_ai("reinforcement_learner")
    
    print(f"Generated Text Classifier: {classifier['name']}")
    print(f"Generated Data Generator: {generator['name']}")
    print(f"Generated Analyzer: {analyzer['name']}")
    print(f"Generated RL Agent: {learner['name']}")
    print(f"\nTotal AIs: {len(core.ai_instances)}")


# ==============================================================================
# EXAMPLE 2: Batch AI Generation
# ==============================================================================

def example_batch_generation():
    """Generate multiple AIs at once"""
    print("\n=== EXAMPLE 2: Batch Generation ===\n")
    
    core = QuantumAICore(name="BatchCore", num_qubits=12)
    
    # Create 10 classifiers
    classifiers = core.create_multi_ai_generation(
        num_ais=10,
        ai_type="text_classifier"
    )
    
    print(f"Generated {len(classifiers)} Text Classifiers")
    for i, ai in enumerate(classifiers[:3]):
        print(f"  {i+1}. {ai['name']} (ID: {ai['id']})")
    print(f"  ... and {len(classifiers) - 3} more")


# ==============================================================================
# EXAMPLE 3: AI Cloning
# ==============================================================================

def example_cloning():
    """Clone successful AIs"""
    print("\n=== EXAMPLE 3: AI Cloning ===\n")
    
    core = QuantumAICore(name="CloningCore")
    
    # Create original AI
    original = core.generate_ai("text_classifier", custom_name="BestClassifier")
    print(f"Original AI: {original['name']} (ID: {original['id']})")
    
    # Clone it multiple times
    clone1 = core.clone_ai(original["id"], new_name="Clone-v1")
    clone2 = core.clone_ai(original["id"], new_name="Clone-v2")
    
    print(f"Clone 1: {clone1['name']}")
    print(f"Clone 2: {clone2['name']}")
    print(f"\nTotal AIs: {len(core.ai_instances)}")


# ==============================================================================
# EXAMPLE 4: AI Entanglement
# ==============================================================================

def example_entanglement():
    """Create entangled AIs for coordination"""
    print("\n=== EXAMPLE 4: AI Entanglement ===\n")
    
    core = QuantumAICore(name="EntanglementCore")
    
    # Create two AIs
    ai1 = core.generate_ai("text_classifier", custom_name="AI-1")
    ai2 = core.generate_ai("analyzer", custom_name="AI-2")
    ai3 = core.generate_ai("data_generator", custom_name="AI-3")
    
    print("Created 3 AIs")
    
    # Entangle them
    core.entangle_ais(ai1["id"], ai2["id"])
    core.entangle_ais(ai2["id"], ai3["id"])
    
    print(f"Entangled {ai1['name']} ↔ {ai2['name']}")
    print(f"Entangled {ai2['name']} ↔ {ai3['name']}")
    print(f"\nEntangled pairs: {core.get_statistics()['entangled_pairs']}")


# ==============================================================================
# EXAMPLE 5: Hierarchical Ecosystem
# ==============================================================================

def example_ecosystem_bootstrap():
    """Create a multi-layer AI ecosystem"""
    print("\n=== EXAMPLE 5: Ecosystem Bootstrap ===\n")
    
    controller = QuantumAIController(system_name="EcosystemDemo")
    
    # Bootstrap 3-layer ecosystem
    ecosystem = controller.initialize_ecosystem(num_layers=3)
    
    print(f"Bootstrapped ecosystem with {ecosystem['total_ais']} AIs")
    for layer in ecosystem['layers']:
        print(f"  Layer {layer['layer']}: {layer['count']} AIs")


# ==============================================================================
# EXAMPLE 6: Task-Specific AI Creation
# ==============================================================================

def example_task_specific():
    """Create AIs tailored to specific tasks"""
    print("\n=== EXAMPLE 6: Task-Specific AI Creation ===\n")
    
    controller = QuantumAIController(system_name="TaskDemo")
    
    # Create AIs for different tasks
    sentiment_ai = controller.spawn_ai_for_task(
        "Classify customer sentiment from reviews"
    )
    
    anomaly_ai = controller.spawn_ai_for_task(
        "Detect anomalies in sensor data"
    )
    
    generator_ai = controller.spawn_ai_for_task(
        "Generate synthetic training data"
    )
    
    print(f"Created AI for Sentiment Analysis: {sentiment_ai['name']}")
    print(f"  Type: {sentiment_ai['type']}")
    print(f"  Task: {sentiment_ai['task_specific']['task']}")
    
    print(f"\nCreated AI for Anomaly Detection: {anomaly_ai['name']}")
    print(f"Created AI for Data Generation: {generator_ai['name']}")


# ==============================================================================
# EXAMPLE 7: AI Networks
# ==============================================================================

def example_networks():
    """Create different AI network topologies"""
    print("\n=== EXAMPLE 7: AI Networks ===\n")
    
    controller = QuantumAIController(system_name="NetworkDemo")
    
    # Create mesh network (fully connected)
    mesh = controller.create_collaborative_network(topology="mesh")
    print(f"Mesh Network: {len(mesh['network_ais'])} AIs, {mesh['connections']} connections")
    
    # Create star network (hub and spoke)
    star = controller.create_collaborative_network(topology="star")
    print(f"Star Network: {len(star['network_ais'])} AIs, {star['connections']} connections")
    
    # Create chain network (sequential)
    chain = controller.create_collaborative_network(topology="chain")
    print(f"Chain Network: {len(chain['network_ais'])} AIs, {chain['connections']} connections")


# ==============================================================================
# EXAMPLE 8: AI Evolution
# ==============================================================================

def example_evolution():
    """Evolve AIs through mutation and crossover"""
    print("\n=== EXAMPLE 8: AI Evolution ===\n")
    
    controller = QuantumAIController(system_name="EvolutionDemo")
    
    # Create parent AIs
    parent1 = controller.spawn_ai_for_task("Task 1")
    parent2 = controller.spawn_ai_for_task("Task 2")
    
    print(f"Parent 1: {parent1['name']}")
    print(f"Parent 2: {parent2['name']}")
    
    # Mutation
    mutated = controller.evolve_ai(parent1["id"], method="mutate")
    print(f"\nMutated AI: {mutated['name']}")
    
    # Crossover
    offspring = controller.evolution_engine.crossover_ais(
        parent1["id"], 
        parent2["id"]
    )
    print(f"Crossover Offspring: {offspring['name']}")
    print(f"  Parents: {offspring['parentage']['parent1']}, {offspring['parentage']['parent2']}")


# ==============================================================================
# EXAMPLE 9: System Monitoring
# ==============================================================================

def example_monitoring():
    """Monitor system status and statistics"""
    print("\n=== EXAMPLE 9: System Monitoring ===\n")
    
    controller = QuantumAIController(system_name="MonitoringDemo")
    controller.initialize_ecosystem(num_layers=2)
    
    status = controller.get_system_status()
    
    print(f"System Name: {status['system_name']}")
    print(f"Meta-AI: {status['meta_ai_name']}")
    
    stats = status['statistics']
    print(f"\nStatistics:")
    print(f"  Total AIs: {stats['total_ais_generated']}")
    print(f"  Total Qubits: {stats['total_qubits']}")
    print(f"  Entangled Pairs: {stats['entangled_pairs']}")
    print(f"\nAI Distribution:")
    for ai_type, count in stats['ais_by_type'].items():
        print(f"  {ai_type}: {count}")


# ==============================================================================
# EXAMPLE 10: State Persistence
# ==============================================================================

def example_persistence():
    """Save and load system state"""
    print("\n=== EXAMPLE 10: State Persistence ===\n")
    
    controller = QuantumAIController(system_name="PersistenceDemo")
    
    # Create some AIs
    controller.initialize_ecosystem(num_layers=2)
    controller.spawn_ai_for_task("Task 1")
    controller.spawn_ai_for_task("Task 2")
    
    # Save state
    import os
    state_file = os.path.join("data", "example_state.json")
    controller.save_system_state(state_file)
    
    print(f"✓ Saved state to: {state_file}")
    
    # Check file size
    file_size = os.path.getsize(state_file)
    print(f"  File size: {file_size} bytes")
    
    status = controller.get_system_status()
    print(f"  AIs in state: {status['statistics']['total_ais_generated']}")


# ==============================================================================
# EXAMPLE 11: Advanced Configuration
# ==============================================================================

def example_advanced_config():
    """Access and modify AI configurations"""
    print("\n=== EXAMPLE 11: Advanced Configuration ===\n")
    
    core = QuantumAICore(name="ConfigCore")
    ai = core.generate_ai("text_classifier")
    
    config = ai['configuration']
    
    print(f"AI: {ai['name']}")
    print(f"\nTraining Configuration:")
    print(f"  Learning Rate: {config['training']['learning_rate']}")
    print(f"  Batch Size: {config['training']['batch_size']}")
    print(f"  Epochs: {config['training']['epochs']}")
    
    print(f"\nOptimization Flags:")
    for flag, value in config['optimization'].items():
        print(f"  {flag}: {value}")


# ==============================================================================
# EXAMPLE 12: API Reference
# ==============================================================================

def example_api_reference():
    """Quick reference to common operations"""
    print("\n=== EXAMPLE 12: API Reference ===\n")
    
    print("Common Operations:")
    print("\n1. Create Controller:")
    print("   controller = QuantumAIController()")
    
    print("\n2. Initialize Ecosystem:")
    print("   ecosystem = controller.initialize_ecosystem(num_layers=3)")
    
    print("\n3. Spawn AI for Task:")
    print("   ai = controller.spawn_ai_for_task('Classify images')")
    
    print("\n4. Create Network:")
    print("   network = controller.create_collaborative_network(topology='mesh')")
    
    print("\n5. Evolve AI:")
    print("   mutated = controller.evolve_ai(ai_id, method='mutate')")
    
    print("\n6. Get Status:")
    print("   status = controller.get_system_status()")
    
    print("\n7. Save State:")
    print("   controller.save_system_state('my_state.json')")
    
    print("\n8. Clone AI:")
    print("   clone = controller.meta_ai.quantum_core.clone_ai(ai_id)")
    
    print("\n9. List AIs:")
    print("   ais = controller.meta_ai.quantum_core.list_ais()")
    
    print("\n10. Get Statistics:")
    print("   stats = controller.meta_ai.quantum_core.get_statistics()")


# ==============================================================================
# Main Execution
# ==============================================================================

def run_all_examples():
    """Run all examples"""
    examples = [
        example_basic_generation,
        example_batch_generation,
        example_cloning,
        example_entanglement,
        example_ecosystem_bootstrap,
        example_task_specific,
        example_networks,
        example_evolution,
        example_monitoring,
        example_persistence,
        example_advanced_config,
        example_api_reference,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    # Uncomment to run specific example:
    # example_basic_generation()
    
    # Or run all examples:
    # run_all_examples()
    
    print("Examples available:")
    print("  1. example_basic_generation()")
    print("  2. example_batch_generation()")
    print("  3. example_cloning()")
    print("  4. example_entanglement()")
    print("  5. example_ecosystem_bootstrap()")
    print("  6. example_task_specific()")
    print("  7. example_networks()")
    print("  8. example_evolution()")
    print("  9. example_monitoring()")
    print("  10. example_persistence()")
    print("  11. example_advanced_config()")
    print("  12. example_api_reference()")
    print("\nRun 'run_all_examples()' to execute all at once")
