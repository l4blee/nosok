import { createSignal, onMount } from 'solid-js'
import { auth } from '../../global_ctx'
import login from '../../assets/icons/login.png'

import classes from './Topbar.module.scss'
import { Link } from '@solidjs/router'

const [isAuth, _] = auth

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
    <div class={classes.Topbar}>
      <div class={classes.Auth}>
        { 
          redirPath() === '/login'
          ?
          <Link href='/login'
                class={classes.LoginButton}>
            <img src={login} alt='login'/>
            <span>{loginButtonLabel}</span>
          </Link> 
          :
          <button class={classes.LoginButton}
                  onClick={() => {window.location.assign('/logout')}}> 
            <img src={login} alt='logout'/>
            <span>{loginButtonLabel}</span>
          </button>
        }
      </div>
    </div>
  )
}
