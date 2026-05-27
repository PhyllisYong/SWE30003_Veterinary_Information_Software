import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import QuizListPage from './pages/QuizListPage'
import QuizPage from './pages/QuizPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

import FirstAidGuides from './pages/FirstAidPage'
function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/quizzes" element={<QuizListPage />} />
        <Route path="/quizzes/:id" element={<QuizPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/guides" element={<FirstAidGuides />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

export default App
