import { GROUND_COLOR } from './constants'

export class Terrain {
  private width: number
  private height: number
  private grid: boolean[][]
  private surfaceHeights: number[]

  constructor(width: number, height: number) {
    this.width = width
    this.height = height
    this.grid = this.generateTerrain()
    this.surfaceHeights = this.calculateSurfaceHeights()
  }

  private generateTerrain(): boolean[][] {
    // Create empty 2D grid (false = air, true = ground)
    const grid: boolean[][] = []
    for (let x = 0; x < this.width; x++) {
      grid[x] = new Array(this.height).fill(false)
    }

    // Generate surface heights
    const heights: number[] = new Array(this.width).fill(Math.floor(this.height * 2/3))
    let currentHeight = heights[0]
    let bias = 0

    for (let i = 1; i < this.width; i++) {
      const step = Math.floor(Math.random() * 82) - 41 + bias
      currentHeight += step
      currentHeight = Math.max(
        this.height / 4,
        Math.min(currentHeight, this.height - 50)
      )

      if (currentHeight < this.height * 0.5) {
        bias = 1
      } else if (currentHeight > this.height * 0.7) {
        bias = -1
      } else {
        bias = 0
      }

      heights[i] = currentHeight
    }

    // Smooth the surface
    const smoothedHeights = this.smoothTerrain(heights, 10)

    // Fill the grid based on surface heights
    for (let x = 0; x < this.width; x++) {
      for (let y = this.height - smoothedHeights[x]; y < this.height; y++) {
        grid[x][y] = true
      }
    }

    // Create some caves
    this.createCaves(grid)

    return grid
  }

  private smoothTerrain(heights: number[], passes: number): number[] {
    let smoothed = [...heights]

    for (let pass = 0; pass < passes; pass++) {
      const newHeights = [...smoothed]
      for (let i = 1; i < smoothed.length - 1; i++) {
        newHeights[i] = Math.floor((smoothed[i - 1] + smoothed[i] + smoothed[i + 1]) / 3)
      }
      smoothed = newHeights
    }

    return smoothed
  }

  private createCaves(grid: boolean[][], numCaves: number = 5) {
    for (let cave = 0; cave < numCaves; cave++) {
      const x = Math.floor(Math.random() * (this.width - 200)) + 100
      let maxY = 0
      for (let y = 0; y < this.height; y++) {
        if (grid[x][y]) {
          maxY = y
          break
        }
      }
      const y = Math.floor(Math.random() * (this.height - maxY - 100)) + maxY + 40

      const caveWidth = Math.floor(Math.random() * 40) + 20
      const caveHeight = Math.floor(Math.random() * 20) + 10

      // Carve out the cave (elliptical shape)
      for (let dx = -caveWidth; dx <= caveWidth; dx++) {
        for (let dy = -caveHeight; dy <= caveHeight; dy++) {
          const nx = x + dx
          const ny = y + dy
          if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
            if ((dx / caveWidth) ** 2 + (dy / caveHeight) ** 2 <= 1) {
              grid[nx][ny] = false
            }
          }
        }
      }

      // Possibly add a tunnel to surface
      if (Math.random() < 0.5) {
        let tunnelY = y - caveHeight
        while (tunnelY > 0 && !grid[x][tunnelY]) {
          tunnelY--
        }
        for (let ty = tunnelY; ty <= y - caveHeight; ty++) {
          for (let tx = x - 4; tx <= x + 4; tx++) {
            if (tx >= 0 && tx < this.width && ty >= 0 && ty < this.height) {
              grid[tx][ty] = false
            }
          }
        }
      }
    }
  }

  private calculateSurfaceHeights(): number[] {
    const heights: number[] = []
    for (let x = 0; x < this.width; x++) {
      for (let y = 0; y < this.height; y++) {
        if (this.grid[x][y]) {
          heights.push(this.height - y)
          break
        }
      }
      if (heights.length <= x) {
        heights.push(0)
      }
    }
    return heights
  }

  public draw(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = GROUND_COLOR
    
    // Draw terrain more efficiently by drawing vertical lines
    for (let x = 0; x < this.width; x++) {
      let startY = -1
      for (let y = 0; y < this.height; y++) {
        if (this.grid[x][y] && startY === -1) {
          startY = y
        } else if (!this.grid[x][y] && startY !== -1) {
          ctx.fillRect(x, startY, 1, y - startY)
          startY = -1
        }
      }
      if (startY !== -1) {
        ctx.fillRect(x, startY, 1, this.height - startY)
      }
    }
  }

  public createExplosion(x: number, y: number, radius: number) {
    // Create circular explosion
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const nx = x + dx
        const ny = y + dy
        if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
          if (dx * dx + dy * dy <= radius * radius) {
            this.grid[nx][ny] = false
          }
        }
      }
    }

    // Update surface heights without sliding
    this.surfaceHeights = this.calculateSurfaceHeights()
  }

  private slideTerrain() {
    for (let x = 0; x < this.width; x++) {
      let count = 0
      for (let y = 0; y < this.height; y++) {
        if (this.grid[x][y]) {
          count++
        }
      }
      
      for (let y = 0; y < this.height; y++) {
        this.grid[x][y] = y >= this.height - count
      }
    }
  }

  public getHeightAt(x: number): number {
    if (x >= 0 && x < this.width) {
      return this.surfaceHeights[x]
    }
    return 0
  }

  public isSolid(x: number, y: number): boolean {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      return this.grid[x][y]
    }
    return false
  }
}