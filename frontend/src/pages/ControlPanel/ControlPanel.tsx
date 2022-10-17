import { onMount } from 'solid-js'

import Sidebar from '../../components/Sidebar/Sidebar'
import Header from '../../components/Header/Header'
import Dashboard from './Dashboard/Dashboard'
import classes from './ControlPanel.module.scss'


export default function ControlPanel() {
  onMount(() => {
    document.title = 'NOSOK | Dashboard'
  })

  return (
    <div class={classes.ControlPanel}>
      <Header/>
      <Sidebar/>
      <Dashboard/>
    </div>
  )
}
