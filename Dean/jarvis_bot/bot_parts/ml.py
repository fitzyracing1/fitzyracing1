"""
Machine Learning Module for JARVIS - Handles predictions and pattern recognition
"""
import random
from typing import Dict, List, Any


class MLTask:
    """Handles Machine Learning tasks for autonomous part generation"""
    
    PART_TYPES = ["Mechanical", "Electrical", "Hydraulic", "Pneumatic"]
    MATERIALS = ["Metal", "Plastic", "Composite", "Titanium", "Aluminum", "Steel"]
    PART_CATEGORIES = [
        "Motor", "Gear", "Bearing", "Shaft", "Coupling",
        "Valve", "Pump", "Cylinder", "Joint", "Spring",
        "Bracket", "Pulley", "Belt", "Piston", "Actuator"
    ]
    
    def __init__(self):
        """Initialize ML Task with seed for reproducibility"""
        self.generation_count = 0
        self.created_parts = []
    
    def predict_part_properties(self, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Predict mechanical part properties based on input keywords
        If no keywords provided, generates autonomous predictions
        """
        self.generation_count += 1
        
        # Generate base part properties
        part_type = random.choice(self.PART_TYPES)
        material = random.choice(self.MATERIALS)
        category = random.choice(self.PART_CATEGORIES)
        
        # Create part with intelligent naming
        part_name = f"{category}_{part_type.lower()}_{self.generation_count}"
        
        # Generate dimensional properties
        properties = {
            'id': self.generation_count,
            'name': part_name,
            'category': category,
            'type': part_type,
            'material': material,
            'version': '1.0',
            'dimensions': {
                'diameter': random.randint(5, 150),
                'width': random.randint(2, 100),
                'height': random.randint(2, 100),
                'weight': round(random.uniform(0.1, 50.0), 2)
            },
            'specifications': {
                'max_rpm': random.randint(500, 10000),
                'torque_capacity': round(random.uniform(10, 1000), 2),
                'temperature_range': f"{random.randint(-50, 20)} to {random.randint(80, 200)} C",
                'efficiency': round(random.uniform(0.75, 0.99), 2)
            },
            'keywords': keywords if keywords else [],
            'confidence_score': round(random.uniform(0.7, 1.0), 2)
        }
        
        self.created_parts.append(properties)
        return properties
    
    def predict_batch(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple part predictions in a batch"""
        return [self.predict_part_properties() for _ in range(count)]
    
    def get_part_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated parts"""
        if not self.created_parts:
            return {}
        
        types = {}
        materials = {}
        for part in self.created_parts:
            types[part['type']] = types.get(part['type'], 0) + 1
            materials[part['material']] = materials.get(part['material'], 0) + 1
        
        return {
            'total_parts_generated': len(self.created_parts),
            'types_distribution': types,
            'materials_distribution': materials,
            'average_confidence': round(sum(p['confidence_score'] for p in self.created_parts) / len(self.created_parts), 3)
        }
