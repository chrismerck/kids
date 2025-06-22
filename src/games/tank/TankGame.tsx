import { useEffect, useRef, useState } from 'react'
import './TankGame.css'
import { Game } from './game/Game'

interface TankGameProps {
  onBackToMenu: () => void
}

function TankGame({ onBackToMenu }: TankGameProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const gameRef = useRef<Game | null>(null)
  const [isGameOver, setIsGameOver] = useState(false)
  const [winner, setWinner] = useState<number | null>(null)

  useEffect(() => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Initialize game
    const game = new Game(ctx, (gameOver, winnerNum) => {
      setIsGameOver(gameOver)
      setWinner(winnerNum)
    })
    gameRef.current = game

    // Start game loop
    game.start()

    // Cleanup
    return () => {
      game.stop()
    }
  }, [])

  const handleRestart = () => {
    if (gameRef.current) {
      gameRef.current.restart()
      setIsGameOver(false)
      setWinner(null)
    }
  }

  return (
    <div className="tank-game">
      <div className="game-header">
        <button className="back-button" onClick={onBackToMenu}>
          ← Back to Menu
        </button>
        <h2>Tank Battle</h2>
      </div>
      
      <div className="game-container">
        <canvas 
          ref={canvasRef}
          width={1600}
          height={1200}
          className="game-canvas"
        />
        
        {isGameOver && (
          <div className="game-over-overlay">
            <div className="game-over-message">
              {winner ? `Player ${winner} Wins!` : 'Game Over!'}
              <button className="restart-button" onClick={handleRestart}>
                Play Again
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="game-controls">
        <div className="controls-info">
          <h3>Controls:</h3>
          <p>← → Arrow Keys: Rotate Barrel</p>
          <p>Space: Fire</p>
        </div>
      </div>
    </div>
  )
}

export default TankGame