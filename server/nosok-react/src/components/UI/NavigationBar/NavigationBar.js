import React from 'react'

import Logo from './Logo/Logo'
import NavButton from './NavButton/NavButton'

import classes from './Sidebar.module.css'

export default function NavigationBar({callback}) {
  return (
    <div className={classes.NavigationBar}>
        <Logo/>
        <nav className={classes.ButtonBar}>
          <NavButton href='/vars' callback={callback}>Overview</NavButton>
          <NavButton href='/log' callback={callback}>Log</NavButton>
        </nav>
    </div>
  )
}
