# GymHelper Frontend (React + Bootstrap)

## Как запустить

1. Перейдите в папку frontend:
   ```bash
   cd frontend
   ```
2. Установите зависимости:
   ```bash
   npm install
   ```
3. Запустите приложение:
   ```bash
   npm start
   ```
4. Откройте [http://localhost:3000](http://localhost:3000) в браузере.

---

- Все данные на страницах — заглушки, чтобы не было ошибок даже без backend.
- Страницы: список тренеров, профиль тренера, тренировки, прогресс.
- Используется Bootstrap для красивого дизайна.

**Если что-то не работает — просто напишите!**

## Features

- View and search for fitness trainers
- View trainer profiles and their workouts
- Track workout progress
- Share progress posts with before/after images
- Like and comment on workouts and progress posts
- Follow trainers

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000.

### Building for Production

To create a production build:

```bash
npm run build
```

The build files will be created in the `build` directory.

## Project Structure

- `src/components/` - React components
- `src/App.js` - Main application component
- `src/index.js` - Application entry point
- `public/` - Static assets

## Technologies Used

- React
- React Router
- React Bootstrap
- Axios
- Bootstrap Icons

## API Integration

The frontend communicates with the backend API running at http://localhost:8000. The proxy is configured in `package.json`.
