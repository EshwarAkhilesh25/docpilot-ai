# DocMind AI - Frontend

A modern, premium AI-powered document intelligence platform frontend built with React, TypeScript, and Vite.

## Tech Stack

- **Framework**: React 18 + TypeScript + Vite
- **Styling**: TailwindCSS + CSS Variables
- **UI Components**: shadcn/ui patterns
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **3D**: React Three Fiber + Three.js + @react-three/drei
- **State Management**: Zustand + TanStack Query
- **Routing**: React Router v7
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Notifications**: Sonner

## Project Structure

```
src/
├── app/                    # Application-level configuration
├── components/
│   ├── common/            # Reusable common components (Button, Card, Loading, etc.)
│   ├── layout/            # Layout components (AuthLayout, DashboardLayout, ChatLayout)
│   ├── ui/                # shadcn/ui components
│   └── three/             # 3D components (ThreeCanvas, SceneLighting)
├── features/              # Feature-based organization (auth, documents, chat, etc.)
├── services/              # API services
├── hooks/                 # Custom React hooks
├── store/                 # Zustand stores (auth, theme, UI)
├── providers/             # React providers (ThemeProvider, QueryProvider)
├── routes/                # Route components (lazy-loaded)
├── types/                 # TypeScript type definitions
├── lib/                   # Utility functions (api, animations, utils)
├── utils/                 # Helper utilities
├── assets/                # Static assets
└── styles/                # Global styles (globals.css)
```

## Design System

### Theme
- **Primary Experience**: Dark mode
- **Secondary**: Light mode
- **Persistence**: LocalStorage
- **System Preference**: Supported

### Color Palette
- Uses HSL values for theme consistency
- CSS variables for dynamic theming
- Semantic color tokens (primary, secondary, muted, accent, destructive)

### Typography
- System font stack with fallbacks
- Font feature settings for ligatures
- Responsive font sizes

### Spacing & Layout
- Tailwind's spacing scale
- Container-based layouts
- Responsive breakpoints (mobile, tablet, desktop)

### Effects
- Glassmorphism utilities
- Gradient borders
- Subtle shadows
- Smooth transitions

### Animation Standards
- Page transitions: 300ms ease-out
- Card animations: 200ms ease-out
- Button hover: 200ms ease-out
- Dialog animations: 200ms ease-out
- Stagger children: 100ms delay

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Lint

```bash
# Run ESLint
npm run lint
```

## Architecture

### State Management
- **Zustand**: Client-side state (auth, theme, UI)
- **TanStack Query**: Server state caching and synchronization

### Routing
- React Router v7 with lazy loading
- Code-splitting for optimal performance
- Route-based code organization

### API Layer
- Axios instance with interceptors
- Automatic token injection
- Error handling and redirects
- Type-safe responses

### 3D Foundation
- React Three Fiber for declarative 3D
- Performance-optimized defaults
- Reusable lighting and camera setups
- Suspense-based loading states

### Component Organization
- Feature-based structure
- No business logic in UI components
- Reusable common components
- Layout components for page structure

## Responsive Design

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

## Development Guidelines

- Use TypeScript strictly
- Follow the existing component patterns
- Keep components small and focused
- Use feature-based organization
- Maintain clean imports with path aliases
- No business logic in UI components

## License

MIT
