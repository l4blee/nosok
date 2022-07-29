import Logo from './Logo'
import Topbar from './Topbar'

import classes from './Header.module.scss'

export default function Header() {
  return (
    <header className={classes.Header}>
        <Logo className={classes.Logo}/>
        <Topbar/>
    </header>
  )
}
