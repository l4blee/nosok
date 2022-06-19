import React from 'react'

import NavButton from './NavButton'
import home from '../icons/home.png'
import control from '../icons/control.png'

import classes from './Sidebar.module.scss'

export default function Sidebar({callback}) {
  return (
      <nav className={classes.Sidebar}>
        <NavButton src={home} href='/vars' callback={callback} alt='home'>Overview</NavButton>  {/* -> Home */}
        <NavButton src={control} href='/log' callback={callback} alt='control'>Log</NavButton>  {/* -> Control */}
      </nav>
  )
}
