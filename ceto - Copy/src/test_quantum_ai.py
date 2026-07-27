"""
Test suite for Quantum AI System
Tests quantum AI generation, evolution, and ecosystem management
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from quantum_ai_core import QuantumAICore, Qubit, AITemplate, QuantumState
from ai_factory import MetaAI, AIFactory, AIEvolutionEngine
from quantum_ai_controller import QuantumAIController


class TestQuantumCore(unittest.TestCase):
    """Test quantum core functionality"""
    
    def setUp(self):
        self.core = QuantumAICore(name="TestCore", num_qubits=8)
    
    def test_initialization(self):
        """Test quantum core initialization"""
        self.assertEqual(len(self.core.qubits), 8)
        self.assertEqual(len(self.core.ai_instances), 0)
        self.assertIn("text_classifier", self.core.ai_templates)
    
    def test_qubit_measurement(self):
        """Test qubit state measurement"""
        qubit = list(self.core.qubits.values())[0]
        measurement = qubit.measure()
        self.assertIsInstance(measurement, bool)
    
    def test_generate_ai(self):
        """Test AI generation"""
        ai = self.core.generate_ai("text_classifier")
        self.assertEqual(ai["type"], "text_classifier")
        self.assertIn("id", ai)
        self.assertEqual(ai["parent_ai"], "TestCore")
    
    def test_generate_multiple_ais(self):
        """Test generating multiple AIs"""
        ais = self.core.create_multi_ai_generation(num_ais=5, ai_type="analyzer")
        self.assertEqual(len(ais), 5)
        self.assertEqual(len(self.core.ai_instances), 5)
    
    def test_entangle_ais(self):
        """Test entangling AIs"""
        ai1 = self.core.generate_ai("text_classifier")
        ai2 = self.core.generate_ai("analyzer")
        
        self.core.entangle_ais(ai1["id"], ai2["id"])
        
        self.assertEqual(self.core.ai_instances[ai1["id"]]["entangled_with"], ai2["id"])
        self.assertEqual(self.core.ai_instances[ai2["id"]]["entangled_with"], ai1["id"])
    
    def test_clone_ai(self):
        """Test cloning an AI"""
        original_ai = self.core.generate_ai("data_generator")
        cloned_ai = self.core.clone_ai(original_ai["id"], new_name="Cloned-AI")
        
        self.assertEqual(cloned_ai["type"], original_ai["type"])
        self.assertEqual(cloned_ai["cloned_from"], original_ai["id"])
        self.assertNotEqual(cloned_ai["id"], original_ai["id"])
    
    def test_statistics(self):
        """Test statistics generation"""
        self.core.generate_ai("text_classifier")
        self.core.generate_ai("analyzer")
        
        stats = self.core.get_statistics()
        self.assertEqual(stats["total_ais_generated"], 2)
        self.assertEqual(stats["total_qubits"], 8)


class TestAIFactory(unittest.TestCase):
    """Test AI factory functionality"""
    
    def setUp(self):
        self.core = QuantumAICore(name="FactoryCore", num_qubits=8)
        self.factory = AIFactory(self.core)
    
    def test_create_ai_batch(self):
        """Test creating batch of AIs"""
        specs = [
            {"type": "text_classifier", "name": "Classifier-1"},
            {"type": "analyzer", "name": "Analyzer-1"},
            {"type": "data_generator", "name": "Generator-1"}
        ]
        
        ais = self.factory.create_ai_batch(specs)
        self.assertEqual(len(ais), 3)
    
    def test_create_specialized_ai(self):
        """Test creating specialized AI"""
        ai = self.factory.create_specialized_ai("sentiment_analyzer", {"threshold": 0.5})
        self.assertEqual(ai["configuration"]["specialization"], "sentiment_analyzer")


class TestMetaAI(unittest.TestCase):
    """Test meta-AI functionality"""
    
    def setUp(self):
        self.meta_ai = MetaAI(name="TestMetaAI")
    
    def test_bootstrap_ecosystem(self):
        """Test bootstrapping AI ecosystem"""
        ecosystem = self.meta_ai.bootstrap_ai_ecosystem(num_layers=2)
        self.assertEqual(len(ecosystem["layers"]), 2)
        self.assertGreater(ecosystem["total_ais"], 0)
    
    def test_create_task_specific_ai(self):
        """Test creating task-specific AI"""
        ai = self.meta_ai.create_task_specific_ai("classification", {"accuracy": 0.95})
        self.assertIn("task_specific", ai)
        self.assertEqual(ai["task_specific"]["task"], "classification")
    
    def test_create_ai_networks(self):
        """Test creating different AI network topologies"""
        mesh_network = self.meta_ai.create_ai_network(topology="mesh")
        star_network = self.meta_ai.create_ai_network(topology="star")
        chain_network = self.meta_ai.create_ai_network(topology="chain")
        
        self.assertGreater(mesh_network["connections"], 0)
        self.assertGreater(star_network["connections"], 0)
        self.assertGreater(chain_network["connections"], 0)


class TestEvolutionEngine(unittest.TestCase):
    """Test AI evolution functionality"""
    
    def setUp(self):
        self.meta_ai = MetaAI(name="EvolutionTest")
        self.engine = AIEvolutionEngine(self.meta_ai)
        self.ai = self.meta_ai.quantum_core.generate_ai("text_classifier")
    
    def test_mutate_ai(self):
        """Test AI mutation"""
        mutated_ai = self.engine.mutate_ai(self.ai["id"], mutation_strength=0.1)
        self.assertNotEqual(mutated_ai["id"], self.ai["id"])
        self.assertIn("Mutated", mutated_ai["name"])
    
    def test_crossover_ais(self):
        """Test AI crossover"""
        ai2 = self.meta_ai.quantum_core.generate_ai("text_classifier")
        offspring = self.engine.crossover_ais(self.ai["id"], ai2["id"])
        
        self.assertIn("parentage", offspring)
        self.assertEqual(offspring["parentage"]["parent1"], self.ai["id"])
        self.assertEqual(offspring["parentage"]["parent2"], ai2["id"])


class TestQuantumAIController(unittest.TestCase):
    """Test main controller functionality"""
    
    def setUp(self):
        self.controller = QuantumAIController(system_name="ControllerTest")
    
    def test_initialization(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.system_name, "ControllerTest")
        self.assertIsNotNone(self.controller.meta_ai)
    
    def test_ecosystem_initialization(self):
        """Test ecosystem initialization"""
        ecosystem = self.controller.initialize_ecosystem(num_layers=2)
        self.assertGreater(ecosystem["total_ais"], 0)
    
    def test_spawn_ai(self):
        """Test spawning AI for task"""
        ai = self.controller.spawn_ai_for_task("Classify images")
        self.assertIn("id", ai)
        self.assertIn("task_specific", ai)
    
    def test_task_classification(self):
        """Test task classification"""
        task_type = QuantumAIController._classify_task("Classify customer data")
        self.assertEqual(task_type, "classification")
    
    def test_system_status(self):
        """Test getting system status"""
        self.controller.initialize_ecosystem(num_layers=1)
        status = self.controller.get_system_status()
        
        self.assertIn("system_name", status)
        self.assertIn("statistics", status)
        self.assertGreater(status["statistics"]["total_ais_generated"], 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumCore))
    suite.addTests(loader.loadTestsFromTestCase(TestAIFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaAI))
    suite.addTests(loader.loadTestsFromTestCase(TestEvolutionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumAIController))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
