import { Tank } from './Tank'
import { Terrain } from './Terrain'
import { Projectile } from './Projectile'
import { SCREEN_WIDTH, SCREEN_HEIGHT, TANK_COLORS, SKY_COLOR } from './constants'

export class Game {
  private ctx: CanvasRenderingContext2D
  private terrain: Terrain
  private tanks: Tank[]
  private currentPlayer: number = 0
  private projectile: Projectile | null = null
  private gameOver: boolean = false
  private winner: number | null = null
  private waitingForProjectile: boolean = false
  private animationId: number | null = null
  private keysPressed: { [key: string]: boolean } = {}
  private onGameOver: (gameOver: boolean, winner: number | null) => void

  constructor(
    ctx: CanvasRenderingContext2D,
    onGameOver: (gameOver: boolean, winner: number | null) => void,
    numPlayers: number = 2
  ) {
    this.ctx = ctx
    this.onGameOver = onGameOver
    
    // Initialize terrain
    this.terrain = new Terrain(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    // Create tanks
    this.tanks = []
    const positions = []
    for (let i = 0; i < numPlayers; i++) {
      positions.push(SCREEN_WIDTH / (numPlayers + 1) * (i + 1))
    }
    
    for (let i = 0; i < numPlayers; i++) {
      this.tanks.push(new Tank(positions[i], this.terrain, TANK_COLORS[i], i + 1))
    }
    
    // Set up event listeners
    this.setupEventListeners()
  }

  private setupEventListeners() {
    window.addEventListener('keydown', this.handleKeyDown)
    window.addEventListener('keyup', this.handleKeyUp)
  }

  private handleKeyDown = (e: KeyboardEvent) => {
    if (this.gameOver || this.waitingForProjectile) return

    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      this.keysPressed[e.key] = true
    } else if (e.key === ' ') {
      this.fire()
    }
  }

  private handleKeyUp = (e: KeyboardEvent) => {
    if (e.key in this.keysPressed) {
      this.keysPressed[e.key] = false
    }
  }

  private fire() {
    if (!this.waitingForProjectile && !this.gameOver) {
      this.projectile = this.tanks[this.currentPlayer].fire()
      this.waitingForProjectile = true
    }
  }

  public start() {
    this.gameLoop()
  }

  public stop() {
    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId)
    }
    window.removeEventListener('keydown', this.handleKeyDown)
    window.removeEventListener('keyup', this.handleKeyUp)
  }

  public restart() {
    this.terrain = new Terrain(SCREEN_WIDTH, SCREEN_HEIGHT)
    const numPlayers = 2 // Fixed number of players for restart
    this.tanks = []
    const positions = []
    for (let i = 0; i < numPlayers; i++) {
      positions.push(SCREEN_WIDTH / (numPlayers + 1) * (i + 1))
    }
    
    for (let i = 0; i < numPlayers; i++) {
      this.tanks.push(new Tank(positions[i], this.terrain, TANK_COLORS[i], i + 1))
    }
    
    this.currentPlayer = 0
    this.projectile = null
    this.gameOver = false
    this.winner = null
    this.waitingForProjectile = false
  }

  private update() {
    // Handle continuous key presses for barrel rotation
    if (!this.waitingForProjectile && !this.gameOver) {
      if (this.keysPressed['ArrowLeft']) {
        this.tanks[this.currentPlayer].rotateBarrel(1)
      }
      if (this.keysPressed['ArrowRight']) {
        this.tanks[this.currentPlayer].rotateBarrel(-1)
      }
    }

    // Update projectile if active
    if (this.waitingForProjectile && this.projectile) {
      if (this.projectile.update(this.terrain, this.tanks)) {
        // Projectile exploded
        this.projectile = null
        this.waitingForProjectile = false
        this.nextPlayer()
      }
    }

    // Check for game over
    let activePlayers = 0
    let lastActive = -1
    for (let i = 0; i < this.tanks.length; i++) {
      if (this.tanks[i].shields > 0) {
        activePlayers++
        lastActive = i
      }
    }

    if (activePlayers <= 1 && this.tanks.length > 1) {
      this.gameOver = true
      this.winner = lastActive >= 0 ? lastActive + 1 : null
      this.onGameOver(true, this.winner)
    }
  }

  private nextPlayer() {
    this.currentPlayer = (this.currentPlayer + 1) % this.tanks.length
    
    // Skip destroyed tanks
    while (this.tanks[this.currentPlayer].shields <= 0) {
      this.currentPlayer = (this.currentPlayer + 1) % this.tanks.length
    }
  }

  private draw() {
    // Clear canvas
    this.ctx.fillStyle = SKY_COLOR
    this.ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    // Draw terrain
    this.terrain.draw(this.ctx)

    // Draw tanks
    for (const tank of this.tanks) {
      tank.draw(this.ctx)
    }

    // Draw projectile
    if (this.projectile) {
      this.projectile.draw(this.ctx)
    }

    // Draw HUD
    this.drawHUD()
  }

  private drawHUD() {
    this.ctx.font = '32px Arial'
    
    // Draw player shields
    for (let i = 0; i < this.tanks.length; i++) {
      const tank = this.tanks[i]
      this.ctx.fillStyle = tank.color
      this.ctx.fillText(
        `Player ${i + 1}: ${tank.shields} shields`,
        40 + i * 400,
        40
      )
    }

    // Highlight current player
    if (!this.gameOver) {
      this.ctx.strokeStyle = 'white'
      this.ctx.lineWidth = 4
      this.ctx.strokeRect(
        30 + this.currentPlayer * 400,
        10,
        380,
        50
      )
    }
  }

  private gameLoop = () => {
    this.update()
    this.draw()
    this.animationId = requestAnimationFrame(this.gameLoop)
  }
}