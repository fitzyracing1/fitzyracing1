import * as THREE from 'three';
import type { MethaneReading } from './methaneData';
import { MethaneDataGenerator } from './methaneData';

export class World3D {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private dataGenerator: MethaneDataGenerator;
  private particles: THREE.Points[] = [];
  private stats: {
    avgReading: number;
    maxReading: number;
    minReading: number;
    lastUpdated: string;
  } = {
    avgReading: 0,
    maxReading: 0,
    minReading: 0,
    lastUpdated: new Date().toLocaleTimeString(),
  };

  constructor(container: HTMLElement) {
    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0a1f);

    // Camera setup
    this.camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    this.camera.position.set(0, 50, 50);
    this.camera.lookAt(0, 0, 0);

    // Renderer setup
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFShadowMap;
    container.appendChild(this.renderer.domElement);

    // Add lighting
    this.setupLighting();

    // Add grid
    this.addGrid();

    // Initialize data generator
    this.dataGenerator = new MethaneDataGenerator();

    // Handle window resize
    window.addEventListener('resize', () => this.onWindowResize(container));

    // Start animation loop
    this.animate();
  }

  private setupLighting(): void {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    // Directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 50, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    this.scene.add(directionalLight);

    // Point lights for methane visualization
    const pointLight1 = new THREE.PointLight(0xff6b6b, 1, 100);
    pointLight1.position.set(30, 30, 30);
    this.scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x4ecdc4, 1, 100);
    pointLight2.position.set(-30, 30, -30);
    this.scene.add(pointLight2);
  }

  private addGrid(): void {
    const gridHelper = new THREE.GridHelper(200, 20, 0x444444, 0x222222);
    gridHelper.position.y = -10;
    this.scene.add(gridHelper);

    // Add axis helper
    const axisHelper = new THREE.AxesHelper(50);
    this.scene.add(axisHelper);
  }

  public updateMethaneData(): void {
    const readings = this.dataGenerator.generateReadings();
    
    // Remove old particles
    this.particles.forEach(particle => this.scene.remove(particle));
    this.particles = [];

    // Calculate statistics
    const values = readings.map(r => r.value);
    this.stats.avgReading = values.reduce((a, b) => a + b, 0) / values.length;
    this.stats.maxReading = Math.max(...values);
    this.stats.minReading = Math.min(...values);
    this.stats.lastUpdated = new Date().toLocaleTimeString();

    // Create particles for each reading
    readings.forEach(reading => {
      this.createParticleForReading(reading);
    });
  }

  private createParticleForReading(reading: MethaneReading): void {
    const geometry = new THREE.BufferGeometry();
    
    // Create particles around the reading point
    const particleCount = Math.ceil(reading.value / 2);
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    // Color based on methane level (red = high, green = low)
    const hue = (1 - reading.value / 100) * 0.3; // 0 = red, 0.3 = green
    const color = new THREE.Color();
    color.setHSL(hue, 1, 0.5);

    for (let i = 0; i < particleCount; i++) {
      // Distribute particles in a sphere around the point
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI * 2;
      const radius = Math.random() * 3;

      positions[i * 3] = reading.x + Math.sin(phi) * Math.cos(theta) * radius;
      positions[i * 3 + 1] = reading.y + Math.cos(phi) * radius;
      positions[i * 3 + 2] = reading.z + Math.sin(phi) * Math.sin(theta) * radius;

      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true,
    });

    const particles = new THREE.Points(geometry, material);
    this.scene.add(particles);
    this.particles.push(particles);
  }

  public getStats() {
    return this.stats;
  }

  private onWindowResize(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = container.clientHeight;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  private animate(): void {
    requestAnimationFrame(() => this.animate());

    // Slowly rotate camera
    const time = Date.now() * 0.0001;
    this.camera.position.x = Math.sin(time) * 80;
    this.camera.position.z = Math.cos(time) * 80;
    this.camera.lookAt(0, 0, 0);

    this.renderer.render(this.scene, this.camera);
  }
}
