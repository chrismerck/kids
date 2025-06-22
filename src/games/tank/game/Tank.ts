import { Terrain } from './Terrain'
import { Projectile } from './Projectile'
import { SCREEN_HEIGHT, SCREEN_WIDTH } from './constants'

export class Tank {
  public x: number
  public y: number = 0
  public shields: number = 5
  public color: string
  public playerNum: number
  
  private terrain: Terrain
  private width: number = 40
  private height: number = 20
  private barrelLength: number = 40
  private barrelAngle: number = 45 // degrees

  constructor(x: number, terrain: Terrain, color: string, playerNum: number) {
    this.x = x
    this.terrain = terrain
    this.color = color
    this.playerNum = playerNum
    this.setPosition(x)
  }

  private setPosition(x: number) {
    this.x = x
    const surfaceHeight = this.terrain.getHeightAt(Math.floor(x))
    this.y = SCREEN_HEIGHT - surfaceHeight - this.height / 2
  }

  public updatePosition() {
    const surfaceHeight = this.terrain.getHeightAt(Math.floor(this.x))
    const targetY = SCREEN_HEIGHT - surfaceHeight - this.height / 2
    
    if (this.y < targetY) {
      this.y = targetY
    }
  }

  public rotateBarrel(direction: number) {
    this.barrelAngle += direction * 2
    this.barrelAngle = Math.max(0, Math.min(this.barrelAngle, 180))
  }

  public move(dx: number) {
    // Calculate the slope at current position
    const currentHeight = this.terrain.getHeightAt(Math.floor(this.x))
    const lookAheadX = this.x + (dx > 0 ? 5 : -5) // Look 5 pixels ahead
    const aheadHeight = this.terrain.getHeightAt(Math.floor(lookAheadX))
    
    // Calculate slope (rise over run)
    const slope = (aheadHeight - currentHeight) / 5
    
    // Adjust horizontal speed based on slope
    // Going uphill (positive slope) reduces speed, downhill increases it slightly
    const slopeFactor = 1 / Math.sqrt(1 + slope * slope) // This gives us the cosine of the slope angle
    const adjustedDx = dx * slopeFactor
    
    // Calculate new position with adjusted speed
    const newX = this.x + adjustedDx
    
    // Keep tank within bounds
    if (newX < this.width / 2 || newX > SCREEN_WIDTH - this.width / 2) {
      return
    }
    
    // Update position
    this.x = newX
    
    // Update Y position to follow terrain
    const surfaceHeight = this.terrain.getHeightAt(Math.floor(this.x))
    this.y = SCREEN_HEIGHT - surfaceHeight - this.height / 2
  }

  private getBarrelEnd(): { x: number; y: number } {
    const angleRad = (this.barrelAngle * Math.PI) / 180
    const barrelX = this.x + Math.cos(angleRad) * this.barrelLength
    const barrelY = this.y - Math.sin(angleRad) * this.barrelLength
    return { x: barrelX, y: barrelY }
  }

  public fire(): Projectile {
    const barrelEnd = this.getBarrelEnd()
    const angleRad = (this.barrelAngle * Math.PI) / 180
    
    const vx = Math.cos(angleRad) * 15 // Match PROJECTILE_SPEED constant
    const vy = -Math.sin(angleRad) * 15
    
    return new Projectile(barrelEnd.x, barrelEnd.y, vx, vy, this.color)
  }

  public damage() {
    this.shields--
    return this.shields <= 0
  }

  public draw(ctx: CanvasRenderingContext2D) {
    if (this.shields <= 0) return // Don't draw destroyed tanks
    
    // Draw tank body
    ctx.fillStyle = this.color
    ctx.fillRect(
      this.x - this.width / 2,
      this.y - this.height / 2,
      this.width,
      this.height
    )

    // Draw barrel
    const barrelEnd = this.getBarrelEnd()
    ctx.strokeStyle = this.color
    ctx.lineWidth = 5
    ctx.beginPath()
    ctx.moveTo(this.x, this.y)
    ctx.lineTo(barrelEnd.x, barrelEnd.y)
    ctx.stroke()

    // Draw shield indicator
    ctx.fillStyle = 'white'
    ctx.font = 'bold 24px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(this.shields.toString(), this.x, this.y - 35)
  }
}