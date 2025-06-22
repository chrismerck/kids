# 9 Lives - Math Game

A fun math game where cats battle dogs using arithmetic operations!

## Requirements

- Python 3.x
- Pygame

## Installation

1. Make sure you have Python installed on your system.
2. Install Pygame:
```
pip install pygame
```

## How to Run

Run the game with the following command:
```
python nine_lives.py
```

## How to Play

### Game Rules:
- On the left side, you have 9 cats arranged in a 3x3 grid, each with a random number (1-9)
- On the right side, there are 2 dogs, each with a random number (1-100)
- The goal is to make the cats fight and defeat all dogs over 9 rounds

### Controls:
1. Click on a cat to select it (its number will be added to your expression)
2. Click on an operation button (+, -, ×) to choose an operation
3. Click on another cat to continue building your expression
4. Repeat steps 2-3 to build longer expressions as needed
5. Click the sword button (⚔️) to attack

### Battle Mechanics:
- If your final calculated value matches the number above a dog, that dog will be defeated
- If your value doesn't match any dog's number, the cats involved in the expression will be defeated
- You win the round if all dogs are defeated
- You lose if all cats are defeated

### Game Progression:
- The game consists of 9 rounds
- New random numbers are generated for each round
- Try to complete all 9 rounds to win the game! 