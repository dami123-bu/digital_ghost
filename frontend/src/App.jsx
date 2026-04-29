import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Chat from './pages/Chat'
import AttackLab from './pages/AttackLab'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Chat />} />
        <Route path="lab" element={<AttackLab />} />
      </Route>
    </Routes>
  )
}
