import { Route, Routes, BrowserRouter } from 'react-router-dom'
import Navbar from './components/Navbar.tsx'
import ErrorPage from './pages/ErrorPage.tsx'
import EvaluatePage from './pages/EvaluatePage.tsx'
import OptimizePage from './pages/OptimizePage.tsx'
import HomePage from './pages/HomePage.tsx'
import Branding from './components/Branding.tsx'
import AppContextProvider from './context.tsx'
import HistoryPage from '@/pages/HistoryPage.tsx'

function App() {
  return (
    <AppContextProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/evaluate" element={<EvaluatePage />} />
          <Route path="/optimize" element={<OptimizePage />} />
          <Route path="/overview" element={<HistoryPage />} />
          <Route path="*" element={<ErrorPage />} />
        </Routes>
        <Branding />
      </BrowserRouter>
    </AppContextProvider>
  )
}

export default App
