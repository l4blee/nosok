import React from 'react'
import Logo from './Logo'

import classes from './Header.module.scss'

export default function Header() {
  return (
    <header className={classes.Header}>
        <Logo className={classes.Logo}/>
        <div className={classes.Topbar}>Topbar</div>
    </header>
  )
}
