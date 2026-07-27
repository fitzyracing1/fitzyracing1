export interface MethaneReading {
  x: number;
  y: number;
  z: number;
  value: number; // PPM (parts per million)
  timestamp: Date;
}

export class MethaneDataGenerator {
  private readings: MethaneReading[] = [];
  private time: number = 0;

  generateReadings(): MethaneReading[] {
    this.readings = [];
    this.time += 0.016; // ~60fps

    // Generate readings at various points in 3D space
    for (let i = 0; i < 10; i++) {
      const angle = (i / 10) * Math.PI * 2;
      const radius = 30;

      // Use Perlin-like noise simulation for realistic variations
      const baseValue = 50 + Math.sin(this.time * 0.5 + i) * 15;
      const variation = Math.sin(this.time * 0.3 + i * 0.5) * 10;
      const localNoise = Math.random() * 10;

      const value = Math.max(0, Math.min(100, baseValue + variation + localNoise));

      this.readings.push({
        x: Math.cos(angle) * radius,
        y: 10 + Math.sin(this.time * 0.2 + i * 0.3) * 5,
        z: Math.sin(angle) * radius,
        value,
        timestamp: new Date(),
      });
    }

    // Add some random isolated readings
    for (let i = 0; i < 5; i++) {
      this.readings.push({
        x: (Math.random() - 0.5) * 80,
        y: Math.random() * 30,
        z: (Math.random() - 0.5) * 80,
        value: 20 + Math.random() * 60,
        timestamp: new Date(),
      });
    }

    return this.readings;
  }

  getReadings(): MethaneReading[] {
    return this.readings;
  }
}
