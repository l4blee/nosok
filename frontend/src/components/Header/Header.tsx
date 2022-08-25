import Logo from './Logo'
import Topbar from './Topbar'

import classes from './Header.module.scss'

export default function Header() {
  return (
    <header class={classes.Header}>
        <Logo class={classes.Logo}/>
        <Topbar/>
    </header>
  )
}
