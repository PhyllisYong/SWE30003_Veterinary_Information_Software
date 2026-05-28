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
import FirstAidGuides from './pages/FirstAidPage'
import Video from './pages/VideoPage'
import VetAdvicePage from './pages/VetAdvicePage'
import ChatPage from './pages/ChatPage'
import BookingPage from './pages/BookingPage'
import VetQuizManagePage from './pages/VetQuizManagePage'
import VetAvailabilityPage from './pages/VetAvailabilityPage'


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
        <Route path="/videos" element={<Video />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/vet-advice" element={<VetAdvicePage />} />
        <Route path="/vet-advice/chat" element={<ChatPage />} />
        <Route path="/vet-advice/booking" element={<BookingPage />} />
        <Route path="/vet/quiz-manage" element={<VetQuizManagePage />} />
        <Route path="/vet/availability" element={<VetAvailabilityPage />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}

export default App
