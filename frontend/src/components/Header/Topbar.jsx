import { createSignal, onMount } from 'solid-js'
import { auth, sid } from '../../global_ctx'
import login from '../../assets/icons/login.png'

import classes from './Topbar.module.scss'
import { Link } from '@solidjs/router'

const [isAuth, __] = auth
const [sID, _] = sid


export default function Topbar() {
  const [redirPath, setRP] = createSignal('')
  const [loginButtonLabel, setLBL] = createSignal('', {equals: false})

  function correlateWithLogin() {
    if (isAuth()) {
      setRP('/auth/logout')
      setLBL('Sign out')
    } else {
      setRP('/login')
      setLBL('Sign in')
    }
  }

  onMount(() => {
    correlateWithLogin()
  })

  return (
    <div className={classes.Topbar}>
      <div className={classes.Auth}>
        {/* {sID() && <span style={'margin-right:15px'}>Session ID: {sID}</span>} */}
        { redirPath() === '/login' ?
          <Link href={redirPath()} className={classes.LoginButton}>
            <img src={login} alt='login'/>
            <span>{loginButtonLabel}</span>
          </Link> :
          <button className={classes.LoginButton} onClick={() => {window.location = redirPath()}}> 
            <img src={login} alt='login'/>
            <span>{loginButtonLabel}</span>
          </button>
        }
      </div>
    </div>
  )
}
