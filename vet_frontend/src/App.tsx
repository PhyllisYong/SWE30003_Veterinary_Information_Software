import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import QuizListPage from './pages/QuizListPage'
import QuizPage from './pages/QuizPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import GuidesPage from './pages/GuidesPage'
import Video from './pages/VideoPage'
import VetAdvicePage from './pages/VetAdvicePage'
import ChatPage from './pages/ChatPage'
import BookingPage from './pages/BookingPage'
import VetQuizManagePage from './pages/VetQuizManagePage'
import VetAvailabilityPage from './pages/VetAvailabilityPage'
import VetVideoManagePage from './pages/VetVideoManagePage'

import ContentManagement from './pages/ContentManagementPage'

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
        <Route path="/guides" element={<GuidesPage />} />
        <Route path="/videos" element={<Video />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/vet-advice" element={<VetAdvicePage />} />
        <Route path="/vet-advice/chat" element={<ChatPage />} />
        <Route path="/vet-advice/booking" element={<BookingPage />} />
        <Route path="/vet/quiz-manage" element={<VetQuizManagePage />} />
        <Route path="/vet/availability" element={<VetAvailabilityPage />} />
        <Route path="/vet/video-manage" element={<VetVideoManagePage />} />
        <Route path="/content-management" element={<ContentManagement />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

export default App
