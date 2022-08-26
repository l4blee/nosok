import { createSignal, onMount } from 'solid-js'
import { Link } from '@solidjs/router'

import classes from './Register.module.scss'


export default function Register() {
  const [form, updateForm] = createSignal<{
    email: string,
    password: string,
    password_retype: string
  }>({
    email: '',
    password: '',
    password_retype: ''
  })

  const [signUpError, setError] = createSignal<{
    state: boolean,
    msg: string
  }>({
    state: false,
    msg: ''
  })

  onMount(() => {
    document.title = 'NOSOK | Sign up'
  })

  function onChange(event: Event) {
    updateForm({
      ...form(),
      [(event.target as HTMLTextAreaElement).name]: (event.target as HTMLTextAreaElement).value
    })
  }

  function submitForm(event: SubmitEvent) {
    event.preventDefault()

    const form_data = form()
    if (form_data.password !== form_data.password_retype) {
      console.log('error');
      setError({
        msg: 'Passwords do not match!',
        state: true
      })
      return;
    }

    fetch(
      '/auth/signup',
      {
        method: 'POST',
        body: JSON.stringify({
          email: form_data.email,
          password: form_data.password
        }),
        headers: {
          'Content-Type': 'application/json'
        },
      }
    ).then(response => {
      if (response.redirected) {
          window.location.href = response.url;
      } else {
        if (response.status !== 200) {
          setError({
            msg: 'An error occured, please try again later.',
            state: true
          })
          return;
        }

        response
        .json()
        .then(data => {
          if (data.message === 'already exists') {
            setError({
              msg: 'A user with this email already exists!',
              state: true
            })
            return
          } 

          setError({
            msg: 'An error occured, please try again later.',
            state: true
          })
        })
      }
    }).catch((_) => setError({
      msg: 'An error occured, please try again later.',
      state: true
    }))
  }

  return (
    <div class={classes.Container}>
      <form class={classes.Form} onSubmit={submitForm}>
        <div class={classes.Content}>
          <header>Sign Up</header>
          { signUpError().state ?
            <div class={classes.error}>{signUpError().msg}</div> :
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
            <input type='password'
                   name='password_retype'
                   required
                   class='form-control mt-1'
                   placeholder='Enter password'
                   onChange={onChange}/>
          </div>
          <div class='mt-3'>
            <label>Repeat your password</label>
            <input type='password'
                   name='password'
                   required
                   class='form-control mt-1'
                   placeholder='Enter password'
                   onPaste={e => e.preventDefault()}
                   onChange={onChange}/>
          </div>
          <div class='mt-3'>
            <button type='submit' class='btn'>
              Submit
            </button>
          </div>
          <div class={`${classes.link} mt-3`}>
            <label>Aleady have an account?</label><Link href='/login'>Login</Link>
          </div>
        </div>
      </form>
    </div>
  )
}