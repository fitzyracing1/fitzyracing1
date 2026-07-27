"""
Multi-Backend Quantum Integration
Supports IonQ and Google Quantum AI backends
Connects Quantum AI System to quantum cloud computing platforms
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import random
import os


class IonQGate(Enum):
    """IonQ-supported quantum gates"""
    X = "x"          # Pauli-X (NOT gate)
    Y = "y"          # Pauli-Y
    Z = "z"          # Pauli-Z
    H = "h"          # Hadamard (superposition)
    CNOT = "cnot"    # Controlled-NOT (entanglement)
    MOLMER_SORENSEN = "ms"  # Mølmer-Sørensen (IonQ native)
    RX = "rx"        # Rotation X
    RY = "ry"        # Rotation Y
    RZ = "rz"        # Rotation Z
    ZZ = "zz"        # ZZ interaction


class IonQNativeGates(Enum):
    """IonQ native gate set (most efficient)"""
    GPI = "gpi"           # Single-qubit rotation
    GPI2 = "gpi2"         # π/2 rotation
    MS = "ms"             # Mølmer-Sørensen entangling gate


@dataclass
class QuantumCircuit:
    """Quantum circuit representation"""
    num_qubits: int
    gates: List[Dict[str, Any]] = None
    measurements: List[int] = None
    
    def __post_init__(self):
        if self.gates is None:
            self.gates = []
        if self.measurements is None:
            self.measurements = list(range(self.num_qubits))
    
    def add_gate(self, gate: str, qubits: List[int], params: Optional[Dict] = None):
        """Add a gate to the circuit"""
        instruction = {
            "gate": gate,
            "targets": qubits,
            "parameters": params or {}
        }
        self.gates.append(instruction)
    
    def to_dict(self):
        return {
            "num_qubits": self.num_qubits,
            "gates": self.gates,
            "measurements": self.measurements
        }


@dataclass
class IonQJob:
    """IonQ job submission"""
    circuit: QuantumCircuit
    shots: int = 1000
    noise_model: str = "ideal"  # ideal, hardware
    target: str = "simulator"   # simulator, hardware
    job_id: Optional[str] = None
    status: str = "created"
    results: Optional[Dict] = None
    
    def to_dict(self):
        return {
            "circuit": self.circuit.to_dict(),
            "shots": self.shots,
            "noise_model": self.noise_model,
            "target": self.target,
            "job_id": self.job_id,
            "status": self.status,
            "results": self.results
        }


class IonQSimulator:
    """
    Local IonQ simulator for development and testing
    Simulates IonQ quantum behavior without cloud API
    """
    
    def __init__(self, num_qubits: int = 8):
        self.num_qubits = num_qubits
        self.state_vector = [0.0] * (2 ** num_qubits)
        self.state_vector[0] = 1.0  # Initialize to |0...0⟩
        self.measurement_results: Dict[int, List[int]] = {}
        self.job_count = 0
    
    def initialize_state(self):
        """Reset to initial state |0...0⟩"""
        self.state_vector = [0.0] * (2 ** self.num_qubits)
        self.state_vector[0] = 1.0
    
    def apply_hadamard(self, qubit: int):
        """Apply Hadamard gate (creates superposition)"""
        # Simplified: mark qubit as in superposition
        pass
    
    def apply_cnot(self, control: int, target: int):
        """Apply CNOT gate (creates entanglement)"""
        # Simplified: mark qubits as entangled
        pass
    
    def apply_molmer_sorensen(self, qubits: List[int], angle: float = 0.0):
        """Apply Mølmer-Sørensen gate (IonQ native)"""
        # IonQ's native entangling gate
        pass
    
    def measure(self, qubits: List[int], shots: int = 1000) -> Dict[str, int]:
        """Simulate measurement"""
        results = {}
        for _ in range(shots):
            # Simulate probabilistic outcome
            outcome = ''.join([str(random.randint(0, 1)) for _ in qubits])
            results[outcome] = results.get(outcome, 0) + 1
        
        return results
    
    def execute_circuit(self, circuit: QuantumCircuit, shots: int = 1000) -> Dict[str, Any]:
        """Execute a quantum circuit"""
        self.initialize_state()
        
        # Apply gates in sequence
        for gate_instruction in circuit.gates:
            gate_type = gate_instruction["gate"]
            qubits = gate_instruction["targets"]
            params = gate_instruction.get("parameters", {})
            
            if gate_type == "h":
                for q in qubits:
                    self.apply_hadamard(q)
            elif gate_type == "cnot":
                if len(qubits) >= 2:
                    self.apply_cnot(qubits[0], qubits[1])
            elif gate_type == "ms":
                self.apply_molmer_sorensen(qubits, params.get("angle", 0.0))
        
        # Perform measurements
        measurements = self.measure(circuit.measurements, shots=shots)
        
        return {
            "measurements": measurements,
            "shots": shots,
            "most_probable": max(measurements, key=measurements.get),
            "success": True
        }


class IonQClient:
    """
    IonQ Quantum Cloud Client
    Interface to IonQ's quantum computing platform
    """
    
    def __init__(self, api_key: Optional[str] = None, use_simulator: bool = True):
        self.api_key = api_key or "mock_api_key"
        self.use_simulator = use_simulator
        self.simulator = IonQSimulator(num_qubits=11)  # IonQ Aria has 11 qubits
        self.jobs: Dict[str, IonQJob] = {}
        self.job_counter = 0
    
    def create_job(self, circuit: QuantumCircuit, shots: int = 1000, 
                   target: str = "simulator", noise_model: str = "ideal") -> IonQJob:
        """Create a quantum job"""
        job = IonQJob(
            circuit=circuit,
            shots=shots,
            noise_model=noise_model,
            target=target
        )
        return job
    
    def submit_job(self, job: IonQJob) -> str:
        """Submit a job to IonQ"""
        self.job_counter += 1
        job_id = f"ionq_job_{self.job_counter}_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
        job.job_id = job_id
        job.status = "submitted"
        
        if self.use_simulator:
            # Execute locally
            results = self.simulator.execute_circuit(job.circuit, shots=job.shots)
            job.results = results
            job.status = "completed"
        else:
            # Would call actual IonQ API here
            job.status = "queued"
        
        self.jobs[job_id] = job
        return job_id
    
    def get_job_status(self, job_id: str) -> str:
        """Get job status"""
        if job_id in self.jobs:
            return self.jobs[job_id].status
        return "not_found"
    
    def get_job_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job results"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status == "completed":
                return job.results
        return None
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs"""
        return [
            {
                "job_id": job_id,
                "status": job.status,
                "shots": job.shots,
                "target": job.target
            }
            for job_id, job in self.jobs.items()
        ]


class IonQQuantumAI:
    """
    Quantum AI integrated with IonQ backend
    Uses real or simulated quantum computing for AI configuration
    """
    
    def __init__(self, api_key: Optional[str] = None, use_simulator: bool = True):
        self.client = IonQClient(api_key=api_key, use_simulator=use_simulator)
        self.quantum_configs: Dict[str, Dict] = {}
    
    def generate_ai_config_quantum(self, num_qubits: int = 8) -> Dict[str, Any]:
        """Generate AI configuration using quantum circuit"""
        circuit = QuantumCircuit(num_qubits=num_qubits)
        
        # Create superposition with Hadamard gates
        for i in range(num_qubits):
            circuit.add_gate("h", [i])
        
        # Create entanglement with CNOT gates
        for i in range(num_qubits - 1):
            circuit.add_gate("cnot", [i, i + 1])
        
        # Submit to IonQ
        job = self.client.create_job(circuit, shots=1000, target="simulator")
        job_id = self.client.submit_job(job)
        
        # Get results
        results = self.client.get_job_results(job_id)
        
        # Convert quantum measurement to AI config
        config = self._convert_measurements_to_config(results, num_qubits)
        self.quantum_configs[job_id] = config
        
        return {
            "job_id": job_id,
            "configuration": config,
            "measurements": results,
            "quantum_source": "IonQ"
        }
    
    def _convert_measurements_to_config(self, measurements: Dict[str, Any], 
                                       num_qubits: int) -> Dict[str, Any]:
        """Convert quantum measurement outcomes to AI configuration"""
        if not measurements:
            return {}
        
        measurement_str = measurements.get("most_probable", "0" * num_qubits)
        bits = [int(b) for b in measurement_str]
        
        # Convert bits to configuration parameters
        config = {
            "learning_rate": 0.001 * (sum(bits) + 1),
            "batch_size": 16 * (sum(bits[::2]) + 1),
            "dropout_rate": 0.1 + (sum(bits[1::2]) / num_qubits * 0.4),
            "use_batch_norm": bits[0] == 1,
            "use_regularization": bits[1] == 1,
            "activation_function": "relu" if bits[2] == 1 else "tanh",
            "optimizer": "adam" if bits[3] == 1 else "sgd",
            "quantum_seed": measurement_str
        }
        
        return config
    
    def get_quantum_config(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve quantum-generated configuration"""
        return self.quantum_configs.get(job_id)


class IonQCloudBackend:
    """
    Full IonQ Cloud Backend
    Manages quantum-classical hybrid AI generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("IONQ_API_KEY")
        self.ionq_ai = IonQQuantumAI(api_key=self.api_key, use_simulator=self.api_key is None)
        self.available_qubits = 11  # IonQ Aria
        self.quantum_overhead = 0.0
        self.backend_name = "IonQ"
    
    def generate_hybrid_ai_config(self, num_qubits: int = 8) -> Dict[str, Any]:
        """Generate AI config using quantum + classical hybrid approach"""
        # Get quantum component
        quantum_result = self.ionq_ai.generate_ai_config_quantum(num_qubits=num_qubits)
        
        # Add classical refinement
        quantum_config = quantum_result["configuration"]
        refined_config = self._refine_config_classically(quantum_config)
        
        return {
            "quantum_component": quantum_result,
            "refined_configuration": refined_config,
            "hybrid_approach": True,
            "backend": self.backend_name
        }
    
    def _refine_config_classically(self, quantum_config: Dict) -> Dict:
        """Apply classical refinement to quantum configuration"""
        refined = quantum_config.copy()
        
        # Clip and optimize values
        refined["learning_rate"] = min(max(refined["learning_rate"], 0.00001), 0.1)
        refined["batch_size"] = max(min(refined["batch_size"], 256), 8)
        refined["dropout_rate"] = min(max(refined["dropout_rate"], 0.0), 0.9)
        
        return refined
    
    def quantum_circuit_to_native_gates(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Convert circuit to IonQ native gate set"""
        native_circuit = QuantumCircuit(num_qubits=circuit.num_qubits)
        
        for gate_instruction in circuit.gates:
            gate = gate_instruction["gate"]
            targets = gate_instruction["targets"]
            params = gate_instruction.get("parameters", {})
            
            # Convert to IonQ native gates (GPI, GPI2, MS)
            if gate == "h":
                # Hadamard = GPI2
                native_circuit.add_gate("gpi2", targets)
            elif gate == "cnot":
                # CNOT using MS gate
                if len(targets) >= 2:
                    native_circuit.add_gate("ms", targets[:2], params)
            elif gate == "ms":
                native_circuit.add_gate("ms", targets, params)
            else:
                # Pass through other gates
                native_circuit.add_gate(gate, targets, params)
        
        return native_circuit
    
    def estimate_execution_cost(self, circuit: QuantumCircuit, 
                               num_shots: int = 1000) -> Dict[str, Any]:
        """Estimate cost of executing on IonQ hardware"""
        # IonQ pricing (per call)
        per_task_cost = 0.30  # USD
        per_shot_cost = 0.0035  # USD per shot
        
        gate_count = len(circuit.gates)
        depth = self._estimate_circuit_depth(circuit)
        
        total_cost = per_task_cost + (num_shots * per_shot_cost)
        
        return {
            "per_task_cost": per_task_cost,
            "per_shot_cost": per_shot_cost,
            "num_shots": num_shots,
            "gate_count": gate_count,
            "circuit_depth": depth,
            "total_cost_usd": total_cost,
            "backend": "IonQ Aria"
        }
    
    def _estimate_circuit_depth(self, circuit: QuantumCircuit) -> int:
        """Estimate circuit depth (simplified)"""
        return len(circuit.gates)
    
    def get_hardware_specs(self) -> Dict[str, Any]:
        """Get IonQ hardware specifications"""
        return {
            "backend_name": "IonQ Aria",
            "qubit_count": 11,
            "native_gates": [
                "gpi",      # Single-qubit rotation
                "gpi2",     # π/2 rotation
                "ms"        # Mølmer-Sørensen entangling gate
            ],
            "max_circuit_depth": 10000,
            "connectivity": "fully_connected",
            "error_rates": {
                "single_qubit": 0.001,  # 0.1% error
                "two_qubit": 0.005      # 0.5% error
            },
            "coherence_time_us": 1000000,
            "gate_time_us": {
                "gpi": 10,
                "gpi2": 10,
                "ms": 170
            }
        }


def create_ionq_quantum_circuit_from_ai_template(ai_template: Dict) -> QuantumCircuit:
    """Convert AI template to quantum circuit"""
    num_qubits = 8
    circuit = QuantumCircuit(num_qubits=num_qubits)
    
    # Map AI parameters to quantum operations
    template_type = ai_template.get("model_type", "classifier")
    
    if template_type == "classifier":
        # Classification: use heavy superposition and entanglement
        for i in range(num_qubits):
            circuit.add_gate("h", [i])
        for i in range(num_qubits - 1):
            circuit.add_gate("cnot", [i, i + 1])
    
    elif template_type == "generator":
        # Generation: lighter superposition
        for i in range(0, num_qubits, 2):
            circuit.add_gate("h", [i])
    
    elif template_type == "analyzer":
        # Analysis: targeted entanglement
        for i in range(0, num_qubits - 1, 2):
            circuit.add_gate("cnot", [i, i + 1])
    
    return circuit


# ============================================================================
# GOOGLE QUANTUM AI BACKEND
# ============================================================================

class GoogleQuantumGate(Enum):
    """Google Quantum AI supported gates"""
    X = "x"
    Y = "y"
    Z = "z"
    H = "h"
    CNOT = "cnot"
    CZ = "cz"           # Controlled-Z (Google native)
    SQRT_X = "sqrt_x"   # Square root of X (Google native)
    SQRT_Y = "sqrt_y"   # Square root of Y
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    FSIM = "fsim"       # fSim gate (Google native)


class GoogleQuantumProcessor(Enum):
    """Google Quantum processors"""
    SYCAMORE = "sycamore"           # 53 qubits
    WEBER = "weber"                 # 53 qubits
    RAINBOW = "rainbow"             # 23 qubits (older)
    SIMULATOR = "simulator"          # Local simulator


@dataclass
class GoogleQuantumJob:
    """Google Quantum AI job"""
    circuit: QuantumCircuit
    processor: str = "simulator"
    shots: int = 1000
    job_id: Optional[str] = None
    status: str = "created"
    results: Optional[Dict] = None
    
    def to_dict(self):
        return {
            "circuit": self.circuit.to_dict(),
            "processor": self.processor,
            "shots": self.shots,
            "job_id": self.job_id,
            "status": self.status,
            "results": self.results
        }


class GoogleQuantumSimulator:
    """
    Google Quantum AI Simulator
    Simulates Google's quantum processors locally
    """
    
    def __init__(self, processor: str = "sycamore"):
        self.processor = processor
        self.num_qubits = 53 if processor in ["sycamore", "weber"] else 23
        self.state_vector = None
        self.job_count = 0
    
    def execute_circuit(self, circuit: QuantumCircuit, shots: int = 1000) -> Dict[str, Any]:
        """Execute quantum circuit with Google-style simulation"""
        # Simplified simulation
        measurements = {}
        
        for _ in range(shots):
            # Simulate measurement outcome
            outcome = ''.join([str(random.randint(0, 1)) for _ in circuit.measurements])
            measurements[outcome] = measurements.get(outcome, 0) + 1
        
        return {
            "measurements": measurements,
            "shots": shots,
            "most_probable": max(measurements, key=measurements.get),
            "processor": self.processor,
            "success": True
        }


class GoogleQuantumClient:
    """
    Google Quantum AI Client
    Interface to Google's Quantum Computing Service
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GOOGLE_QUANTUM_API_KEY")
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.use_simulator = self.api_key is None
        self.simulator = GoogleQuantumSimulator(processor="sycamore")
        self.jobs: Dict[str, GoogleQuantumJob] = {}
        self.job_counter = 0
    
    def create_job(self, circuit: QuantumCircuit, processor: str = "simulator", 
                   shots: int = 1000) -> GoogleQuantumJob:
        """Create a quantum job for Google backend"""
        job = GoogleQuantumJob(
            circuit=circuit,
            processor=processor,
            shots=shots
        )
        return job
    
    def submit_job(self, job: GoogleQuantumJob) -> str:
        """Submit job to Google Quantum AI"""
        self.job_counter += 1
        job_id = f"google_quantum_{self.job_counter}_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
        job.job_id = job_id
        job.status = "submitted"
        
        if self.use_simulator or job.processor == "simulator":
            # Execute locally
            results = self.simulator.execute_circuit(job.circuit, shots=job.shots)
            job.results = results
            job.status = "completed"
        else:
            # Would call actual Google Quantum API here
            job.status = "queued"
        
        self.jobs[job_id] = job
        return job_id
    
    def get_job_status(self, job_id: str) -> str:
        """Get job status"""
        if job_id in self.jobs:
            return self.jobs[job_id].status
        return "not_found"
    
    def get_job_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job results"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status == "completed":
                return job.results
        return None
    
    def list_processors(self) -> List[Dict[str, Any]]:
        """List available Google quantum processors"""
        return [
            {
                "name": "sycamore",
                "qubits": 53,
                "topology": "grid",
                "native_gates": ["sqrt_x", "sqrt_y", "cz", "fsim"],
                "availability": "limited"
            },
            {
                "name": "weber",
                "qubits": 53,
                "topology": "grid",
                "native_gates": ["sqrt_x", "sqrt_y", "cz", "fsim"],
                "availability": "limited"
            },
            {
                "name": "simulator",
                "qubits": 53,
                "topology": "full",
                "native_gates": ["all"],
                "availability": "always"
            }
        ]


class GoogleQuantumAI:
    """
    Google Quantum AI for AI configuration generation
    Uses Google's quantum processors for AI hyperparameter generation
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        self.client = GoogleQuantumClient(api_key=api_key, project_id=project_id)
        self.quantum_configs: Dict[str, Dict] = {}
    
    def generate_ai_config_quantum(self, num_qubits: int = 8, 
                                   processor: str = "simulator") -> Dict[str, Any]:
        """Generate AI configuration using Google quantum circuit"""
        circuit = QuantumCircuit(num_qubits=num_qubits)
        
        # Create superposition with Hadamard gates
        for i in range(num_qubits):
            circuit.add_gate("h", [i])
        
        # Create entanglement with CZ gates (Google native)
        for i in range(num_qubits - 1):
            circuit.add_gate("cz", [i, i + 1])
        
        # Submit to Google Quantum
        job = self.client.create_job(circuit, processor=processor, shots=1000)
        job_id = self.client.submit_job(job)
        
        # Get results
        results = self.client.get_job_results(job_id)
        
        # Convert quantum measurement to AI config
        config = self._convert_measurements_to_config(results, num_qubits)
        self.quantum_configs[job_id] = config
        
        return {
            "job_id": job_id,
            "configuration": config,
            "measurements": results,
            "quantum_source": "Google Quantum AI",
            "processor": processor
        }
    
    def _convert_measurements_to_config(self, measurements: Dict[str, Any], 
                                       num_qubits: int) -> Dict[str, Any]:
        """Convert quantum measurement outcomes to AI configuration"""
        if not measurements:
            return {}
        
        measurement_str = measurements.get("most_probable", "0" * num_qubits)
        bits = [int(b) for b in measurement_str]
        
        # Convert bits to configuration parameters
        config = {
            "learning_rate": 0.0001 * (sum(bits) + 1),
            "batch_size": 8 * (sum(bits[::2]) + 1),
            "dropout_rate": 0.1 + (sum(bits[1::2]) / num_qubits * 0.4),
            "use_batch_norm": bits[0] == 1,
            "use_regularization": bits[1] == 1,
            "activation_function": "relu" if bits[2] == 1 else "gelu",
            "optimizer": "adam" if bits[3] == 1 else "adamw",
            "quantum_seed": measurement_str,
            "epochs": 50 + sum(bits) * 10
        }
        
        return config


class GoogleQuantumBackend:
    """
    Full Google Quantum AI Backend
    Manages quantum-classical hybrid AI generation with Google processors
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GOOGLE_QUANTUM_API_KEY")
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.google_ai = GoogleQuantumAI(api_key=self.api_key, project_id=self.project_id)
        self.available_qubits = 53  # Sycamore/Weber
        self.backend_name = "Google Quantum AI"
    
    def generate_hybrid_ai_config(self, num_qubits: int = 8, 
                                  processor: str = "simulator") -> Dict[str, Any]:
        """Generate AI config using Google quantum + classical hybrid approach"""
        # Get quantum component
        quantum_result = self.google_ai.generate_ai_config_quantum(
            num_qubits=num_qubits,
            processor=processor
        )
        
        # Add classical refinement
        quantum_config = quantum_result["configuration"]
        refined_config = self._refine_config_classically(quantum_config)
        
        return {
            "quantum_component": quantum_result,
            "refined_configuration": refined_config,
            "hybrid_approach": True,
            "backend": self.backend_name,
            "processor": processor
        }
    
    def _refine_config_classically(self, quantum_config: Dict) -> Dict:
        """Apply classical refinement to quantum configuration"""
        refined = quantum_config.copy()
        
        # Clip and optimize values
        refined["learning_rate"] = min(max(refined["learning_rate"], 0.00001), 0.1)
        refined["batch_size"] = max(min(refined["batch_size"], 256), 8)
        refined["dropout_rate"] = min(max(refined["dropout_rate"], 0.0), 0.9)
        refined["epochs"] = min(max(refined["epochs"], 10), 200)
        
        return refined
    
    def get_hardware_specs(self) -> Dict[str, Any]:
        """Get Google Quantum AI hardware specifications"""
        return {
            "backend_name": "Google Quantum AI",
            "processors": [
                {
                    "name": "Sycamore",
                    "qubit_count": 53,
                    "topology": "2D grid",
                    "native_gates": ["sqrt_x", "sqrt_y", "cz", "fsim"],
                    "gate_time_ns": {
                        "single_qubit": 25,
                        "two_qubit": 32
                    },
                    "error_rates": {
                        "single_qubit": 0.0015,  # 0.15%
                        "two_qubit": 0.006       # 0.6%
                    }
                },
                {
                    "name": "Weber",
                    "qubit_count": 53,
                    "topology": "2D grid",
                    "native_gates": ["sqrt_x", "sqrt_y", "cz", "fsim"],
                    "gate_time_ns": {
                        "single_qubit": 25,
                        "two_qubit": 32
                    },
                    "error_rates": {
                        "single_qubit": 0.0015,
                        "two_qubit": 0.006
                    }
                }
            ],
            "api_access": "google_cloud_project_required"
        }
    
    def estimate_execution_cost(self, circuit: QuantumCircuit, 
                               num_shots: int = 1000) -> Dict[str, Any]:
        """Estimate cost of executing on Google Quantum AI"""
        # Google Quantum Engine pricing (estimated)
        per_second_cost = 0.25  # USD per second
        gate_execution_time_us = len(circuit.gates) * 50  # ~50 µs per gate
        total_time_seconds = (gate_execution_time_us * num_shots) / 1_000_000
        
        total_cost = per_second_cost * total_time_seconds
        
        return {
            "per_second_cost": per_second_cost,
            "execution_time_seconds": total_time_seconds,
            "num_shots": num_shots,
            "gate_count": len(circuit.gates),
            "total_cost_usd": max(0.01, total_cost),  # Minimum $0.01
            "backend": "Google Quantum AI",
            "note": "Estimated pricing, actual costs may vary"
        }


# ============================================================================
# UNIFIED QUANTUM BACKEND
# ============================================================================

class UnifiedQuantumBackend:
    """
    Unified backend supporting multiple quantum cloud providers
    Automatically selects backend based on available API keys
    """
    
    def __init__(self, ionq_api_key: Optional[str] = None,
                 google_api_key: Optional[str] = None,
                 google_project_id: Optional[str] = None,
                 preferred_backend: str = "auto"):
        
        self.ionq_api_key = ionq_api_key or os.environ.get("IONQ_API_KEY")
        self.google_api_key = google_api_key or os.environ.get("GOOGLE_QUANTUM_API_KEY")
        self.google_project_id = google_project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        
        # Initialize backends
        self.ionq_backend = IonQCloudBackend(api_key=self.ionq_api_key)
        self.google_backend = GoogleQuantumBackend(
            api_key=self.google_api_key,
            project_id=self.google_project_id
        )
        
        # Select active backend
        self.active_backend = self._select_backend(preferred_backend)
        self.backend_name = self.active_backend.backend_name
    
    def _select_backend(self, preferred: str):
        """Select backend based on availability and preference"""
        if preferred == "google" or (preferred == "auto" and self.google_api_key):
            print(f"[Quantum Backend] Using Google Quantum AI")
            return self.google_backend
        elif preferred == "ionq" or (preferred == "auto" and self.ionq_api_key):
            print(f"[Quantum Backend] Using IonQ")
            return self.ionq_backend
        else:
            # Default to Google simulator
            print(f"[Quantum Backend] Using Google Quantum AI (simulator)")
            return self.google_backend
    
    def generate_hybrid_ai_config(self, num_qubits: int = 8, **kwargs) -> Dict[str, Any]:
        """Generate AI config using active quantum backend"""
        return self.active_backend.generate_hybrid_ai_config(num_qubits=num_qubits, **kwargs)
    
    def get_hardware_specs(self) -> Dict[str, Any]:
        """Get hardware specs from active backend"""
        return self.active_backend.get_hardware_specs()
    
    def estimate_execution_cost(self, circuit: QuantumCircuit, num_shots: int = 1000) -> Dict[str, Any]:
        """Estimate cost using active backend"""
        if hasattr(self.active_backend, 'estimate_execution_cost'):
            return self.active_backend.estimate_execution_cost(circuit, num_shots)
        return {"cost": "N/A", "backend": self.backend_name}
    
    def switch_backend(self, backend_name: str):
        """Switch to different backend"""
        if backend_name.lower() == "google":
            self.active_backend = self.google_backend
            self.backend_name = "Google Quantum AI"
            print(f"[Quantum Backend] Switched to Google Quantum AI")
        elif backend_name.lower() == "ionq":
            self.active_backend = self.ionq_backend
            self.backend_name = "IonQ"
            print(f"[Quantum Backend] Switched to IonQ")
    
    def list_available_backends(self) -> List[Dict[str, Any]]:
        """List all available backends"""
        return [
            {
                "name": "Google Quantum AI",
                "available": self.google_api_key is not None,
                "qubits": 53,
                "status": "active" if self.active_backend == self.google_backend else "available"
            },
            {
                "name": "IonQ",
                "available": self.ionq_api_key is not None,
                "qubits": 11,
                "status": "active" if self.active_backend == self.ionq_backend else "available"
            }
        ]
