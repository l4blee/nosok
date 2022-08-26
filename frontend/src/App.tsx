import { lazy } from 'solid-js'
import { Routes, Route } from '@solidjs/router'

const ControlPanel = lazy(() => import('./pages/ControlPanel/ControlPanel'))
const Login = lazy(() => import('./pages/Auth/Login'))
const Register = lazy(() => import('./pages/Auth/Register'))


export default function App() {
  return (
    <Routes>
      <Route path='/' component={ControlPanel}/>
      <Route path='/login' component={Login}/>
      <Route path='/register' component={Register}/>
    </Routes>
  )
}