import { useState } from 'react'
import './App.css'
import { Route } from 'react-router'

function App() {
  const [count, setCount] = useState(0)

  return (
    <Routes>
      <Route path="/" element={<HomePage/>} />
      <Route path ="/login" element={<LoginPage/>} />
      <Route path ="/signup" element={<SignUpPage/>} />
    </Routes>
  )
}

export default App
