import { Routes, Route } from '@solidjs/router'
import { lazy } from 'solid-js'

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
