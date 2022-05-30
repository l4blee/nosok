import React from 'react'
import logo from './logo.png'
import classes from './Logo.module.css'

export default function Logo({children, ...props}) {
  return (
    <div className={classes.Logo}>
      <img src={logo} alt='logo'/>
      <div>NOSOK</div>
    </div>
  )
};
