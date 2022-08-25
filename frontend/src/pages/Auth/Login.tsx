import { createSignal, onMount } from 'solid-js'
import classes from './Login.module.scss'
import visible from '../../assets/icons/visible.png'
import invisible from '../../assets/icons/invisible.png'
import { Link } from '@solidjs/router'


export default function Login() {
  const [form, updateForm] = createSignal({
    email: null,
    password: null
  })

  const [showPwd, setShowPwd] = createSignal(false)
  const [unauthErr, setUnauthErr] = createSignal(false)

  onMount(() => {
    document.title = 'NOSOK | Sign in'
  })

  function onChange(event: Event) {
    updateForm({
      ...form(),
      [(event.target as HTMLTextAreaElement).name]: (event.target as HTMLTextAreaElement).value
    })
  }

  function submitForm(event: SubmitEvent) {
    event.preventDefault()
    
    fetch(
      '/auth/signin',
      {
        method: 'POST',
        body: JSON.stringify(form()),
        headers: {
          'Content-Type': 'application/json'
        },
      }
    ).then(response => {
      if (response.redirected) {
          window.location.href = response.url;
      } else {
        setUnauthErr(true)
      }
    })
    .catch((_) => setUnauthErr(true))
  }

  return (
    <div class={classes.Container}>
      <form class={classes.Form} onSubmit={submitForm}>
        <div class={classes.Content}>
          <header>Sign In</header>
          { unauthErr() ?
            <div class={classes.error}>There was a problem with your login.</div> :
            '' 
          }
          <div>
            <label>Email</label>
            <input type='email'
                   name='email'
                   required
                   class='form-control mt-1'
                   placeholder='Enter email'
                   onChange={onChange}/>
          </div>
          <div class='mt-3'>
            <label>Password</label>
            <label class={`${classes.password} mt-1`}>
              <input type={showPwd() ? 'text' : 'password'}
                    name='password'
                    required
                    class='form-control'
                    placeholder='Enter password'
                    onChange={onChange}/>
              <label>
                <input type='checkbox' onChange={(_) => setShowPwd(!showPwd())}/>
                <img src={showPwd() ? visible : invisible} alt='show'/>
              </label>
            </label>
          </div>
          <div class='mt-3'>
            <button type='submit' class='btn'>
              Submit
            </button>
          </div>
          <div class={`${classes.link} mt-3`}>
            <label>New to NOSOK?</label><Link href='/register'>Sign up</Link>
          </div>
          <div class={`${classes.link} mt-2`}>
            {/* <a href='#'>Forgot password?</a> TODO: forgot password */}
          </div>
        </div>
      </form>
    </div>
  )
}