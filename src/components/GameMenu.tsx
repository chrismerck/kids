import './GameMenu.css'

interface GameMenuProps {
  onGameSelect: (game: 'tank') => void
}

function GameMenu({ onGameSelect }: GameMenuProps) {
  return (
    <div className="game-menu">
      <h1 className="menu-title">Kids Games</h1>
      <div className="games-grid">
        <button 
          className="game-button tank-button"
          onClick={() => onGameSelect('tank')}
        >
          <div className="game-icon">🎮</div>
          <span className="game-name">Tank Battle</span>
        </button>
      </div>
    </div>
  )
}

export default GameMenu