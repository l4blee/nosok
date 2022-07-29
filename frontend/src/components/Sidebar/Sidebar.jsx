import NavButton from './NavButton'

// Importing icons
import home from '../../assets/icons/home.png'
import control from '../../assets/icons/control.png'

import classes from './Sidebar.module.scss'

export default function Sidebar({callback}) {
  return (
      <nav className={classes.Sidebar}>
        <NavButton src={home} alt='home' href='/vars' callback={callback}>Overview</NavButton> {/* -> Home */}
        <NavButton src={control} alt='control' href='/log' callback={callback}>Log</NavButton>  {/* -> Control */}
      </nav>
  )
}
