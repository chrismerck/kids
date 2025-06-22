# Kids Games

A collection of fun browser-based games for kids, built with React and TypeScript.

## Available Games

- **Tank Battle** - A classic artillery game where players take turns firing projectiles at each other

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Deployment

This project is automatically deployed to GitHub Pages at https://chrismerck.github.io/kids/ when changes are pushed to the main branch.

## Adding New Games

To add a new game:

1. Create a new folder in `src/games/`
2. Implement your game component
3. Add a button for your game in `src/components/GameMenu.tsx`
4. Update the `App.tsx` to handle routing to your new game

## Technology Stack

- React
- TypeScript
- Vite
- HTML5 Canvas
- GitHub Pages