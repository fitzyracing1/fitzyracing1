"""
Multi-Backend Quantum AI Integration
Bridges the Quantum AI System with IonQ and Google Quantum AI backends
"""

from quantum_ai_controller import QuantumAIController
from quantum_ai_core import QuantumAICore
from ionq_backend import (
    UnifiedQuantumBackend, QuantumCircuit,
    create_ionq_quantum_circuit_from_ai_template
)
from typing import Dict, Any, Optional, List


class QuantumIntegratedController(QuantumAIController):
    """
    Extended Quantum AI Controller with multi-backend quantum support
    Supports IonQ and Google Quantum AI
    """
    
    def __init__(self, system_name: str = "Quantum-AI-Multi-Backend",
                 ionq_api_key: Optional[str] = None,
                 google_api_key: Optional[str] = None,
                 google_project_id: Optional[str] = None,
                 preferred_backend: str = "auto"):
        super().__init__(system_name=system_name)
        
        self.quantum_backend = UnifiedQuantumBackend(
            ionq_api_key=ionq_api_key,
            google_api_key=google_api_key,
            google_project_id=google_project_id,
            preferred_backend=preferred_backend
        )
        
        self.quantum_jobs = {}
        self.quantum_generated_ais = {}
        print(f"[{system_name}] Initialized with {self.quantum_backend.backend_name}")
    
    def generate_ai_with_quantum(self, ai_type: str, num_qubits: int = 8) -> Dict[str, Any]:
        """
        Generate AI using quantum backend (Google or IonQ)
        Configuration parameters derived from quantum circuit execution
        """
        backend_name = self.quantum_backend.backend_name
        print(f"\n[Quantum Integration] Generating {ai_type} AI using {backend_name}...")
        
        # Generate hybrid quantum-classical config
        hybrid_config = self.quantum_backend.generate_hybrid_ai_config(num_qubits=num_qubits)
        
        # Create base AI from template
        base_ai = self.meta_ai.quantum_core.generate_ai(ai_type)
        
        # Enhance with quantum configuration
        base_ai["quantum_enhanced"] = True
        base_ai["quantum_integration"] = {
            "job_id": hybrid_config["quantum_component"]["job_id"],
            "quantum_measurements": hybrid_config["quantum_component"]["measurements"],
            "quantum_seed": hybrid_config["refined_configuration"].get("quantum_seed"),
            "backend": backend_name,
            "processor": hybrid_config["quantum_component"].get("processor", "N/A")
        }
        
        # Override configuration with quantum-derived values
        quantum_params = hybrid_config["refined_configuration"]
        base_ai["configuration"]["training"]["learning_rate"] = quantum_params.get("learning_rate", 0.01)
        base_ai["configuration"]["training"]["batch_size"] = int(quantum_params.get("batch_size", 32))
        base_ai["configuration"]["training"]["epochs"] = int(quantum_params.get("epochs", 100))
        
        base_ai["configuration"]["optimization"]["use_dropout"] = quantum_params.get("use_regularization", False)
        base_ai["configuration"]["optimization"]["use_batch_norm"] = quantum_params.get("use_batch_norm", False)
        
        self.quantum_generated_ais[base_ai["id"]] = hybrid_config
        
        print(f"✓ Created quantum-enhanced AI: {base_ai['name']}")
        print(f"  - Backend: {backend_name}")
        print(f"  - Quantum Job ID: {hybrid_config['quantum_component']['job_id']}")
        print(f"  - Learning Rate: {quantum_params.get('learning_rate', 0.01):.6f}")
        print(f"  - Batch Size: {quantum_params.get('batch_size', 32)}")
        
        return base_ai
    
    def batch_quantum_ai_generation(self, num_ais: int = 5, ai_type: str = "text_classifier") -> list:
        """Generate multiple AIs using quantum backend"""
        backend_name = self.quantum_backend.backend_name
        print(f"\n[Quantum Integration] Batch generating {num_ais} {ai_type} AIs with {backend_name}...")
        
        ais = []
        for i in range(num_ais):
            ai = self.generate_ai_with_quantum(ai_type, num_qubits=8)
            ais.append(ai)
        
        print(f"✓ Generated {len(ais)} quantum-enhanced AIs")
        return ais
    
    def get_quantum_job_info(self, ai_id: str) -> Optional[Dict[str, Any]]:
        """Get quantum job information for an AI"""
        return self.quantum_generated_ais.get(ai_id)
    
    def get_hardware_capabilities(self) -> Dict[str, Any]:
        """Get quantum hardware capabilities"""
        return self.quantum_backend.get_hardware_specs()
    
    def list_available_backends(self) -> List[Dict[str, Any]]:
        """List all available quantum backends"""
        return self.quantum_backend.list_available_backends()
    
    def switch_backend(self, backend_name: str):
        """Switch quantum backend"""
        self.quantum_backend.switch_backend(backend_name)
        print(f"[{self.system_name}] Switched to {self.quantum_backend.backend_name}")


# Keep old name for compatibility
IonQIntegratedController = QuantumIntegratedController


def demonstrate_quantum_integration():
    """Demonstrate multi-backend quantum integration"""
    print("\n" + "="*70)
    print("Multi-Backend Quantum AI Integration Demo")
    print("="*70)
    
    # Create controller with auto backend selection
    controller = QuantumIntegratedController(
        system_name="Quantum-AI-Demo",
        preferred_backend="auto"  # Will use Google if API key available
    )
    
    # Phase 1: List available backends
    print("\n[PHASE 1] Available Quantum Backends")
    print("-" * 70)
    backends = controller.list_available_backends()
    for backend in backends:
        status_icon = "✓" if backend["status"] == "active" else "○"
        available_text = "Available" if backend["available"] else "Not Available (API Key Required)"
        print(f"{status_icon} {backend['name']}: {backend['qubits']} qubits - {available_text}")
    
    # Phase 2: Get hardware info
    print("\n[PHASE 2] Quantum Hardware Capabilities")
    print("-" * 70)
    specs = controller.get_hardware_capabilities()
    print(f"Backend: {specs.get('backend_name', 'N/A')}")
    
    if 'processors' in specs:
        # Google backend
        for proc in specs['processors']:
            print(f"\nProcessor: {proc['name']}")
            print(f"  Qubits: {proc['qubit_count']}")
            print(f"  Topology: {proc['topology']}")
            print(f"  Native Gates: {', '.join(proc['native_gates'])}")
            if 'error_rates' in proc:
                print(f"  Error Rates:")
                print(f"    - Single-qubit: {proc['error_rates']['single_qubit']*100:.2f}%")
                print(f"    - Two-qubit: {proc['error_rates']['two_qubit']*100:.2f}%")
    else:
        # IonQ backend
        print(f"Qubits: {specs.get('qubit_count', 'N/A')}")
        print(f"Native Gates: {', '.join(specs.get('native_gates', []))}")
        print(f"Connectivity: {specs.get('connectivity', 'N/A')}")
    
    # Phase 3: Generate single quantum-enhanced AI
    print("\n[PHASE 3] Quantum-Enhanced AI Generation")
    print("-" * 70)
    
    ai1 = controller.generate_ai_with_quantum("text_classifier", num_qubits=8)
    print(f"\nGenerated: {ai1['name']}")
    print(f"Type: {ai1['type']}")
    print(f"Quantum Enhanced: {ai1.get('quantum_enhanced', False)}")
    print(f"Backend: {ai1['quantum_integration']['backend']}")
    
    quantum_info = controller.get_quantum_job_info(ai1["id"])
    if quantum_info:
        print(f"Quantum Measurements: {quantum_info['quantum_component']['measurements']['most_probable']}")
    
    # Phase 4: Batch quantum generation
    print("\n[PHASE 4] Batch Quantum-Enhanced AI Generation")
    print("-" * 70)
    
    batch_ais = controller.batch_quantum_ai_generation(num_ais=3, ai_type="analyzer")
    print(f"\nBatch generated {len(batch_ais)} analyzer AIs")
    for ai in batch_ais:
        learning_rate = ai['configuration']['training']['learning_rate']
        batch_size = ai['configuration']['training']['batch_size']
        print(f"  - {ai['name']}: LR={learning_rate:.6f}, BatchSize={batch_size}")
    
    # Phase 5: System status
    print("\n[PHASE 5] System Status")
    print("-" * 70)
    
    status = controller.get_system_status()
    stats = status['statistics']
    
    print(f"Total AIs Generated: {stats['total_ais_generated']}")
    print(f"Quantum-Enhanced AIs: {len(controller.quantum_generated_ais)}")
    print(f"Distribution:")
    for ai_type, count in stats['ais_by_type'].items():
        print(f"  - {ai_type}: {count}")
    
    # Phase 6: Hybrid ecosystem
    print("\n[PHASE 6] Hybrid Quantum-Classical Ecosystem")
    print("-" * 70)
    
    # Create ecosystem with quantum-enhanced AIs
    print("\nInitializing quantum-enhanced ecosystem...")
    ecosystem = controller.initialize_ecosystem(num_layers=2)
    print(f"Created ecosystem with {ecosystem['total_ais']} classical AIs")
    
    # Add quantum-enhanced AIs
    print("\nAdding quantum-enhanced AIs to ecosystem...")
    quantum_ais = controller.batch_quantum_ai_generation(num_ais=2, ai_type="text_classifier")
    print(f"Added {len(quantum_ais)} quantum-enhanced AIs")
    
    final_status = controller.get_system_status()
    final_stats = final_status['statistics']
    
    print(f"\nFinal Statistics:")
    print(f"  Total AIs: {final_stats['total_ais_generated']}")
    print(f"  Quantum-Enhanced: {len(controller.quantum_generated_ais)}")
    print(f"  Classical: {final_stats['total_ais_generated'] - len(controller.quantum_generated_ais)}")
    print(f"  Active Backend: {controller.quantum_backend.backend_name}")
    
    # Phase 7: Save hybrid ecosystem
    print("\n[PHASE 7] Saving Hybrid Ecosystem")
    print("-" * 70)
    
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    os.makedirs(data_dir, exist_ok=True)
    controller.save_system_state(os.path.join(data_dir, "quantum_hybrid_ecosystem.json"))
    print("✓ Saved hybrid ecosystem to data/quantum_hybrid_ecosystem.json")
    
    print("\n" + "="*70)
    print(f"Quantum Integration Demo Complete!")
    print(f"Active Backend: {controller.quantum_backend.backend_name}")
    print("="*70)
    
    return controller


# Compatibility aliases
demonstrate_ionq_integration = demonstrate_quantum_integration


if __name__ == "__main__":
    from typing import List
    controller = demonstrate_quantum_integration()
