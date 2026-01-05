# Frontend Implementation Plan: Elecantro

## 1. Project Setup & Dependencies
- **Stack**: React (Vite), TailwindCSS.
- **Key Libraries**:
  - `axios`: API requests.
  - `@tanstack/react-query`: Server state management & polling.
  - `recharts`: Beautiful visualizations.
  - `framer-motion`: Smooth animations.
  - `lucide-react`: Iconic interface elements.
  - `react-hook-form`: Form handling.
  - `react-router-dom`: Navigation.

## 2. Design System (Foundation)
- **Theme**: Dark mode by default (Modern SaaS look).
- **Colors**: Deep indigo/violet accents against slate/black backgrounds.
- **Typography**: Inter (Clean sans-serif).
- **Components to Build**:
  - `Button` (Variants: Primary/Glass/Ghost)
  - `Card` (Glassmorphism effect)
  - `Input`/`Select` (Styled form elements)
  - `Badge` (Status indicators)
  - `ProgressBar` (Animated)

## 3. Auth Module
- **Pages**: Login, Register.
- **Features**: JWT storage in localStorage, Axios interceptor for Auto-Attach Token.

## 4. Main Application Structure
- **Layout**: Sidebar navigation + Topbar (Entity Switcher).
- **Protected Routes**: Redirect to login if no token.

## 5. Core Feature: Data Ingestion (Upload)
- **Page**: `/upload`
- **UI**:
  - Drag & Drop Zone (Visual feedback).
  - "Recent Batches" list with **Real-time Progress Bars** (polling every 2s).

## 6. Core Feature: Dashboard
- **Page**: `/dashboard`
- **Widgets**:
  - **KPI Cards**: Total Feedback, Sentiment Score, Critical Alerts.
  - **Charts**: 
    - Sentiment Trend (Line Chart).
    - Topic Distribution (Bar Chart).
  - **Recent Activity**: Stream of latest processed feedback.

## 7. Core Feature: Insights & Analysis
- **Page**: `/insights`
- **UI**:
  - Kanban or List view of AI-generated insights.
  - Filtering by Severity (Critical/High).
  - Detail View: Drill down into specific feedback clusters.

## 8. Polish
- **Animations**: Page transitions, entry animations for charts.
- **Loading States**: Shimmer/Skeleton effects (Crucial for perceived performance).
