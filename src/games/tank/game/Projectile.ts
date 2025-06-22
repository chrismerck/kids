import { Terrain } from './Terrain'
import { Tank } from './Tank'
import { GRAVITY, SCREEN_WIDTH, SCREEN_HEIGHT, EXPLOSION_RADIUS, MIN_KINETIC_ENERGY } from './constants'

export class Projectile {
  public x: number
  public y: number
  public active: boolean = true
  
  private vx: number
  private vy: number
  private color: string
  private radius: number = 6
  private explosionFrame: number = 0
  private explosionX: number = 0
  private explosionY: number = 0

  constructor(x: number, y: number, vx: number, vy: number, color: string) {
    this.x = x
    this.y = y
    this.vx = vx
    this.vy = vy
    this.color = color
  }

  public update(terrain: Terrain, tanks: Tank[]): boolean {
    if (!this.active) return false

    // Handle explosion animation
    if (this.explosionFrame > 0) {
      this.explosionFrame++
      if (this.explosionFrame > 30) { // Animation lasts 30 frames
        return true // Explosion finished
      }
      return false
    }

    // Apply gravity
    this.vy += GRAVITY

    // Store old position for collision detection
    const oldX = this.x
    const oldY = this.y

    // Update position
    this.x += this.vx
    this.y += this.vy

    // Check for wall collisions
    if (this.x < this.radius) {
      this.x = this.radius
      this.vx = -this.vx * 0.7
    } else if (this.x >= SCREEN_WIDTH - this.radius) {
      this.x = SCREEN_WIDTH - this.radius
      this.vx = -this.vx * 0.7
    }

    if (this.y < this.radius) {
      this.y = this.radius
      this.vy = -this.vy * 0.7
    }

    // Check for tank collisions first
    for (const tank of tanks) {
      if (tank.shields > 0) {
        const distance = Math.sqrt((tank.x - this.x) ** 2 + (tank.y - this.y) ** 2)
        if (distance < 30) { // Hit tank
          this.explode(terrain, tanks)
          return false
        }
      }
    }

    // Check for terrain collision with line tracing
    const steps = Math.ceil(Math.max(Math.abs(this.vx), Math.abs(this.vy)) * 2)
    for (let i = 1; i <= steps; i++) {
      const t = i / steps
      const checkX = oldX + (this.x - oldX) * t
      const checkY = oldY + (this.y - oldY) * t
      
      if (terrain.isSolid(Math.floor(checkX), Math.floor(checkY))) {
        // Found collision point, now calculate bounce
        const shouldExplode = this.bounceOffTerrain(terrain, oldX, oldY, checkX, checkY)
        if (shouldExplode) {
          this.explode(terrain, tanks)
        }
        return false
      }
    }

    // Check if projectile is out of bounds
    if (this.y > SCREEN_HEIGHT + 100) {
      this.active = false
      return true
    }

    return false
  }

  private bounceOffTerrain(terrain: Terrain, oldX: number, oldY: number, collisionX: number, collisionY: number): boolean {
    // Back up to just before collision
    this.x = oldX
    this.y = oldY

    // Calculate terrain normal by sampling nearby points
    const normal = this.calculateTerrainNormal(terrain, Math.floor(collisionX), Math.floor(collisionY))
    
    // Calculate reflection vector with energy loss
    const dot = this.vx * normal.x + this.vy * normal.y
    this.vx = (this.vx - 2 * dot * normal.x) * 0.7 // 30% energy loss
    this.vy = (this.vy - 2 * dot * normal.y) * 0.7

    // Check kinetic energy after bounce
    const kineticEnergy = 0.5 * (this.vx * this.vx + this.vy * this.vy)
    if (kineticEnergy < MIN_KINETIC_ENERGY) {
      // Too slow after bounce, explode
      return true
    }

    // Move slightly away from collision point
    this.x += normal.x * 2
    this.y += normal.y * 2
    return false
  }

  private calculateTerrainNormal(terrain: Terrain, x: number, y: number): { x: number; y: number } {
    // Sample surrounding points to estimate surface normal
    const samples = [
      { dx: -1, dy: 0 }, { dx: 1, dy: 0 },
      { dx: 0, dy: -1 }, { dx: 0, dy: 1 },
      { dx: -1, dy: -1 }, { dx: 1, dy: -1 },
      { dx: -1, dy: 1 }, { dx: 1, dy: 1 }
    ]
    
    let nx = 0, ny = 0
    for (const sample of samples) {
      if (!terrain.isSolid(x + sample.dx, y + sample.dy)) {
        nx += sample.dx
        ny += sample.dy
      }
    }
    
    // Normalize
    const length = Math.sqrt(nx * nx + ny * ny)
    if (length > 0) {
      nx /= length
      ny /= length
    } else {
      // Default to up if no clear normal
      nx = 0
      ny = -1
    }
    
    return { x: nx, y: ny }
  }

  private explode(terrain: Terrain, tanks: Tank[]) {
    // Start explosion animation
    this.explosionFrame = 1
    this.explosionX = this.x
    this.explosionY = this.y

    // Modify terrain
    terrain.createExplosion(Math.floor(this.x), Math.floor(this.y), EXPLOSION_RADIUS)

    // Check if any tanks are in blast radius
    for (const tank of tanks) {
      const distance = Math.sqrt((tank.x - this.x) ** 2 + (tank.y - this.y) ** 2)
      if (distance < EXPLOSION_RADIUS) {
        tank.damage()
      }
    }

    // Update tank positions after terrain changes
    for (const tank of tanks) {
      tank.updatePosition()
    }
  }

  public draw(ctx: CanvasRenderingContext2D) {
    if (this.explosionFrame > 0) {
      // Draw explosion animation
      const progress = this.explosionFrame / 30
      const maxRadius = EXPLOSION_RADIUS * 1.5
      
      // Draw multiple circles for fire effect
      for (let i = 0; i < 3; i++) {
        const radius = maxRadius * progress * (1 - i * 0.2)
        const alpha = 1 - progress
        
        const gradient = ctx.createRadialGradient(
          this.explosionX, this.explosionY, 0,
          this.explosionX, this.explosionY, radius
        )
        
        if (i === 0) {
          gradient.addColorStop(0, `rgba(255, 255, 0, ${alpha})`) // Yellow center
          gradient.addColorStop(0.5, `rgba(255, 127, 0, ${alpha * 0.8})`) // Orange
          gradient.addColorStop(1, `rgba(255, 0, 0, 0)`) // Red edge
        } else if (i === 1) {
          gradient.addColorStop(0, `rgba(255, 200, 0, ${alpha * 0.6})`)
          gradient.addColorStop(1, `rgba(255, 50, 0, 0)`)
        } else {
          gradient.addColorStop(0, `rgba(255, 100, 0, ${alpha * 0.3})`)
          gradient.addColorStop(1, `rgba(200, 0, 0, 0)`)
        }
        
        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(this.explosionX, this.explosionY, radius, 0, Math.PI * 2)
        ctx.fill()
      }
    } else if (this.active) {
      // Draw projectile
      ctx.fillStyle = this.color
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
      ctx.fill()
      
      // Add a trail effect
      ctx.fillStyle = this.color + '44' // Semi-transparent
      ctx.beginPath()
      ctx.arc(this.x - this.vx * 0.5, this.y - this.vy * 0.5, this.radius * 0.7, 0, Math.PI * 2)
      ctx.fill()
    }
  }
}