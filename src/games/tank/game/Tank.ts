import { Terrain } from './Terrain'
import { Projectile } from './Projectile'
import { SCREEN_HEIGHT } from './constants'

export class Tank {
  public x: number
  public y: number
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
    console.log(`Tank ${this.playerNum} positioned at (${this.x}, ${this.y}), surface height: ${surfaceHeight}`)
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

  private getBarrelEnd(): { x: number; y: number } {
    const angleRad = (this.barrelAngle * Math.PI) / 180
    const barrelX = this.x + Math.cos(angleRad) * this.barrelLength
    const barrelY = this.y - Math.sin(angleRad) * this.barrelLength
    return { x: barrelX, y: barrelY }
  }

  public fire(): Projectile {
    const barrelEnd = this.getBarrelEnd()
    const angleRad = (this.barrelAngle * Math.PI) / 180
    
    const vx = Math.cos(angleRad) * 20
    const vy = -Math.sin(angleRad) * 20
    
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