import React, { useContext } from 'react'
import classes from './NavButton.module.css'
import DataContext from '../../DataContext'

export default function NavButton({children, ...props}) {
  const [, setContent] = useContext(DataContext)

  async function redirect() {
    let data = await fetch('/api' + props.href)
              .then(res => res.json())
              .catch(e => {})
        
    if (data['content'] === 'vars') {
      setContent(data['data']['status'])
    } else if (data['content'] === 'log') {
      let log = data['data'].replace('\n', '<br>')
      setContent(
        <div>
          {`${log}`}
        </div>
      )
    }
  }

  return (
    <div className={classes.NavButton} onClick={redirect}>
        <span>{children}</span>
    </div>
  )
}
