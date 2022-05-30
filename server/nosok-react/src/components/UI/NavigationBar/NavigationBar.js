import React from 'react'

import Logo from './Logo/Logo'
import NavButton from './NavButton/NavButton'

import classes from './Sidebar.module.css'

export default function NavigationBar() {
  return (
    <div className={classes.NavigationBar}>
        <Logo/>
        <nav className={classes.ButtonBar}>
          <NavButton href='/vars'>Overview</NavButton>
          <NavButton href='/log'>Log</NavButton>
        </nav>
    </div>
  )
}
