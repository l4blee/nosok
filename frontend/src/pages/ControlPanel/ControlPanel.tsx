import { onMount } from 'solid-js'

import Sidebar from '../../components/Sidebar/Sidebar'
import Header from '../../components/Header/Header'
import Content from './Content/Content'
import classes from './ControlPanel.module.scss'


export default function ControlPanel() {
  onMount(() => {
    document.title = 'NOSOK | Dashboard'
  })

  return (
    <div class={classes.ControlPanel}>
      <Header/>
      <Sidebar/>
      <Content/>
    </div>
  )
}
