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

  function onChange(event) {
    updateForm({
      ...form(),
      [event.target.name]: event.target.value,
    })
  }

  function submitForm(event) {
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
    <div className={classes.Container}>
      <form className={classes.Form} onSubmit={submitForm}>
        <div className={classes.Content}>
          <header>Sign In</header>
          { unauthErr() ?
            <div className={classes.error}>There was a problem with your login.</div> :
            '' 
          }
          <div>
            <label>Email</label>
            <input type='email'
                   name='email'
                   required
                   className='form-control mt-1'
                   placeholder='Enter email'
                   onChange={onChange}/>
          </div>
          <div className='mt-3'>
            <label>Password</label>
            <label className={`${classes.password} mt-1`}>
              <input type={showPwd() ? 'text' : 'password'}
                    name='password'
                    required
                    className='form-control'
                    placeholder='Enter password'
                    onChange={onChange}/>
              <label>
                <input type='checkbox' onChange={(_) => setShowPwd(!showPwd())}/>
                <img src={showPwd() ? visible : invisible} alt='show'/>
              </label>
            </label>
          </div>
          <div className='mt-3'>
            <button type='submit' className='btn'>
              Submit
            </button>
          </div>
          <div className={`${classes.link} mt-3`}>
            <label>New to NOSOK?</label><Link href='/register'>Sign up</Link>
          </div>
          <div className={`${classes.link} mt-2`}>
            {/* <a href='#'>Forgot password?</a> TODO: forgot password */}
          </div>
        </div>
      </form>
    </div>
  )
}