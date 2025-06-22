import { Terrain } from './Terrain'
import { Tank } from './Tank'
import { GRAVITY, SCREEN_WIDTH, EXPLOSION_RADIUS } from './constants'

export class Projectile {
  public x: number
  public y: number
  public active: boolean = true
  
  private vx: number
  private vy: number
  private color: string
  private radius: number = 6

  constructor(x: number, y: number, vx: number, vy: number, color: string) {
    this.x = x
    this.y = y
    this.vx = vx
    this.vy = vy
    this.color = color
  }

  public update(terrain: Terrain, tanks: Tank[]): boolean {
    if (!this.active) return false

    // Apply gravity
    this.vy += GRAVITY

    // Store old position for collision detection
    const oldX = this.x
    const oldY = this.y

    // Update position
    this.x += this.vx
    this.y += this.vy

    // Check for wall/ceiling collisions
    if (this.x < 0) {
      this.x = 0
      this.vx = -this.vx * 0.8
    } else if (this.x >= SCREEN_WIDTH) {
      this.x = SCREEN_WIDTH - 1
      this.vx = -this.vx * 0.8
    }

    if (this.y < 0) {
      this.y = 0
      this.vy = -this.vy * 0.8
    }

    // Check for terrain collision
    const xInt = Math.floor(this.x)
    const yInt = Math.floor(this.y)

    if (terrain.isSolid(xInt, yInt)) {
      this.explode(terrain, tanks)
      return true
    }

    // Check for line collision between old and new position
    if (Math.abs(this.vx) > 1 || Math.abs(this.vy) > 1) {
      const steps = Math.floor(Math.max(Math.abs(this.vx), Math.abs(this.vy))) * 2
      for (let i = 1; i <= steps; i++) {
        const t = i / steps
        const checkX = Math.floor(oldX + (this.x - oldX) * t)
        const checkY = Math.floor(oldY + (this.y - oldY) * t)
        if (terrain.isSolid(checkX, checkY)) {
          this.x = checkX
          this.y = checkY
          this.explode(terrain, tanks)
          return true
        }
      }
    }

    return false
  }

  private explode(terrain: Terrain, tanks: Tank[]) {
    this.active = false

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
    if (this.active) {
      ctx.fillStyle = this.color
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
      ctx.fill()
    }
  }
}