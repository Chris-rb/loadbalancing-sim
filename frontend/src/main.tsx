import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import SimDashboard from './SimDashboard.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SimDashboard />
  </StrictMode>,
)
