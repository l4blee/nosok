import React from 'react'
import classes from './NavButton.module.css'

export default function NavButton({children, href, callback}) {
  async function redirect() {
    let data = await fetch('/api' + href)
              .then(res => res.json())
              .catch(e => {})
    
    let output = ''
    if (data === undefined) {callback(output); return}

    if (href === '/vars') output = JSON.stringify(data['content'], null, 4)
    else if (href === '/log') output = data['content']
    console.log(output)
    
    callback(output)
  }

  return (
    <div className={classes.NavButton} onClick={redirect}>
        <span>{children}</span>
    </div>
  )
}
