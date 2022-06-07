import React from 'react'

import Logo from './Logo'
import NavButton from './NavButton'
import overview from './icons/home.png'
import log from './icons/news.png'

import classes from './Sidebar.module.css'

export default function NavigationBar({callback}) {
  return (
    <div className={classes.NavigationBar}>
        <Logo className={classes.Logo}/>
        <nav className={classes.ButtonBar}>
          <NavButton src={overview} className={classes.NavButton} href='/vars' callback={callback}>Overview</NavButton>
          <NavButton src={log}className={classes.NavButton} href='/log' callback={callback}>Log</NavButton>
        </nav>
    </div>
  )
}
