import { useState } from 'react'
import './App.css'
import GameMenu from './components/GameMenu'
import TankGame from './games/tank/TankGame'

type GameType = 'menu' | 'tank'

function App() {
  const [currentGame, setCurrentGame] = useState<GameType>('menu')

  const handleGameSelect = (game: GameType) => {
    setCurrentGame(game)
  }

  const handleBackToMenu = () => {
    setCurrentGame('menu')
  }

  return (
    <div className="app">
      {currentGame === 'menu' && (
        <GameMenu onGameSelect={handleGameSelect} />
      )}
      {currentGame === 'tank' && (
        <TankGame onBackToMenu={handleBackToMenu} />
      )}
    </div>
  )
}

export default App