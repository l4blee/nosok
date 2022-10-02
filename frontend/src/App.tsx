import { lazy } from 'solid-js'
import { Routes, Route } from '@solidjs/router'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)
Chart.defaults.font = {
    family: 'Montserrat',
    size: 14
}

Chart.overrides['doughnut'].plugins.legend = {
  ...Chart.overrides['doughnut'].plugins.legend,
  display: false
}

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