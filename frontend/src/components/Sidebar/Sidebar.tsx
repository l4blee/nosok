import NavButton from './NavButton'

import home from '../../assets/icons/home.png'
import control from '../../assets/icons/control.png'

import classes from './Sidebar.module.scss'

export default function Sidebar() {
  return (
      <nav class={classes.Sidebar}>
        <NavButton src={home} alt='dashboard' navigate='dashboard'>Dashboard</NavButton>
        <NavButton src={control} alt='logs' navigate='logs'>Logs</NavButton>
      </nav>
  )
}
