"""
Quantum AI Controller - Main execution and control interface
Orchestrates the entire quantum AI ecosystem
"""

from ai_factory import MetaAI, AIFactory, AIEvolutionEngine
from quantum_ai_core import QuantumAICore
import json
from datetime import datetime
from typing import Dict, Any


class QuantumAIController:
    """Main controller for quantum AI system"""
    
    def __init__(self, system_name: str = "QuantumAI-Master"):
        self.system_name = system_name
        self.meta_ai = MetaAI(name=f"MetaAI-{system_name}")
        self.evolution_engine = AIEvolutionEngine(self.meta_ai)
        self.execution_log: list = []
    
    def initialize_ecosystem(self, num_layers: int = 3) -> Dict[str, Any]:
        """Initialize a complete AI ecosystem"""
        print(f"[{self.system_name}] Initializing AI ecosystem...")
        
        ecosystem = self.meta_ai.bootstrap_ai_ecosystem(num_layers=num_layers)
        
        self.execution_log.append({
            "action": "initialize_ecosystem",
            "timestamp": datetime.now().isoformat(),
            "result": ecosystem
        })
        
        return ecosystem
    
    def spawn_ai_for_task(self, task_description: str) -> Dict[str, Any]:
        """Spawn a new AI to handle a specific task"""
        print(f"[{self.system_name}] Spawning AI for task: {task_description}")
        
        # Classify the task
        task_type = self._classify_task(task_description)
        requirements = self._extract_requirements(task_description)
        
        # Create specialized AI
        ai = self.meta_ai.create_task_specific_ai(task_type, requirements)
        
        self.execution_log.append({
            "action": "spawn_ai",
            "task": task_description,
            "task_type": task_type,
            "ai_id": ai["id"],
            "timestamp": datetime.now().isoformat()
        })
        
        return ai
    
    def create_collaborative_network(self, topology: str = "mesh") -> Dict[str, Any]:
        """Create a network of AIs that work together"""
        print(f"[{self.system_name}] Creating collaborative AI network with {topology} topology...")
        
        network = self.meta_ai.create_ai_network(topology=topology)
        
        self.execution_log.append({
            "action": "create_network",
            "topology": topology,
            "timestamp": datetime.now().isoformat(),
            "result": network
        })
        
        return network
    
    def evolve_ai(self, ai_id: str, method: str = "mutate") -> Dict[str, Any]:
        """Evolve an AI through mutation or crossover"""
        print(f"[{self.system_name}] Evolving AI {ai_id} using {method}...")
        
        if method == "mutate":
            evolved_ai = self.evolution_engine.mutate_ai(ai_id, mutation_strength=0.15)
        else:
            # Find another AI to crossover with
            all_ais = self.meta_ai.quantum_core.list_ais()
            if len(all_ais) < 2:
                raise ValueError("Need at least 2 AIs for crossover")
            
            other_ai = next((ai for ai in all_ais if ai["id"] != ai_id), None)
            if not other_ai:
                raise ValueError("No suitable AI found for crossover")
            
            evolved_ai = self.evolution_engine.crossover_ais(ai_id, other_ai["id"])
        
        self.execution_log.append({
            "action": "evolve_ai",
            "ai_id": ai_id,
            "method": method,
            "evolved_ai_id": evolved_ai["id"],
            "timestamp": datetime.now().isoformat()
        })
        
        return evolved_ai
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        status = self.meta_ai.get_ecosystem_status()
        status["system_name"] = self.system_name
        status["execution_log_size"] = len(self.execution_log)
        
        return status
    
    def save_system_state(self, filepath: str):
        """Save entire system state"""
        state = {
            "system_name": self.system_name,
            "meta_ai_name": self.meta_ai.name,
            "ecosystem_status": self.meta_ai.get_ecosystem_status(),
            "execution_log": self.execution_log
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"System state saved to {filepath}")
    
    @staticmethod
    def _classify_task(description: str) -> str:
        """Classify task based on description"""
        keywords = {
            "classification": ["classify", "categorize", "sort", "identify"],
            "generation": ["generate", "create", "produce", "synthesize"],
            "analysis": ["analyze", "examine", "analyze", "study"],
            "decision": ["decide", "choose", "optimize", "plan"],
        }
        
        description_lower = description.lower()
        for task_type, keywords_list in keywords.items():
            if any(keyword in description_lower for keyword in keywords_list):
                return task_type
        
        return "analysis"  # Default
    
    @staticmethod
    def _extract_requirements(description: str) -> Dict[str, Any]:
        """Extract requirements from task description"""
        return {
            "raw_description": description,
            "priority": "high" if "urgent" in description.lower() else "normal",
            "complexity": "high" if any(word in description.lower() for word in ["complex", "difficult", "advanced"]) else "normal"
        }


def main():
    """Demo of the quantum AI system"""
    print("=" * 60)
    print("QUANTUM AI SYSTEM - AI Building AI")
    print("=" * 60)
    
    # Create controller
    controller = QuantumAIController(system_name="QuantumAI-Master")
    
    # Initialize ecosystem
    print("\n[PHASE 1] Initializing AI Ecosystem...")
    ecosystem = controller.initialize_ecosystem(num_layers=3)
    print(f"Created {ecosystem['total_ais']} AIs across {len(ecosystem['layers'])} layers")
    
    # Spawn specific AIs for tasks
    print("\n[PHASE 2] Spawning Task-Specific AIs...")
    task_ai_1 = controller.spawn_ai_for_task("Classify customer sentiment from reviews")
    task_ai_2 = controller.spawn_ai_for_task("Generate synthetic training data")
    task_ai_3 = controller.spawn_ai_for_task("Analyze anomalies in sensor data")
    
    print(f"Spawned AI: {task_ai_1['name']} (ID: {task_ai_1['id']})")
    print(f"Spawned AI: {task_ai_2['name']} (ID: {task_ai_2['id']})")
    print(f"Spawned AI: {task_ai_3['name']} (ID: {task_ai_3['id']})")
    
    # Create collaborative network
    print("\n[PHASE 3] Creating Collaborative AI Network...")
    topology = "mesh"
    network = controller.create_collaborative_network(topology=topology)
    print(f"Created {topology} network with {network['connections']} connections")
    
    # Evolve AIs
    print("\n[PHASE 4] Evolving AIs...")
    mutated_ai = controller.evolve_ai(task_ai_1["id"], method="mutate")
    print(f"Created mutated AI: {mutated_ai['name']}")
    
    # Get system status
    print("\n[PHASE 5] System Status...")
    status = controller.get_system_status()
    print(f"Total AIs generated: {status['statistics']['total_ais_generated']}")
    print(f"AIs by type: {status['statistics']['ais_by_type']}")
    
    # Save state
    print("\n[PHASE 6] Saving System State...")
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    os.makedirs(data_dir, exist_ok=True)
    controller.save_system_state(os.path.join(data_dir, "quantum_ai_state.json"))
    
    # Display all generated AIs
    print("\n[SUMMARY] All Generated AIs:")
    print("-" * 60)
    for ai_info in status["all_ais"]:
        print(f"  - {ai_info['name']:25} | Type: {ai_info['type']:20} | Status: {ai_info['status']}")
    
    print("\n" + "=" * 60)
    print("Quantum AI System Ready!")
    print("=" * 60)
    
    return controller


if __name__ == "__main__":
    from typing import Dict, Any
    controller = main()
