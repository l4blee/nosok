import React from 'react'
import classes from './NavButton.module.css'

export default function NavButton({children, href, callback}) {
  return (
    <div className={classes.NavButton} onClick={() => callback(href)}>
        <span>{children}</span>
    </div>
  )
}
