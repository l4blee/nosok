import React, { useState } from 'react'
import NavigationBar from './components/UI/NavigationBar/NavigationBar'
import Content from './components/UI/Content'
import useInterval from './utils'

import classes from './App.module.css'

export default function App() {
  const [content, setContent] = useState()
  const [href, setHref] = useState('')

  async function fetchAPI() {
    if (href === '') return ''
    let response = await fetch('/api' + href)
                        .then(res => res.json())
                        
    if (response === undefined) return ''
                        
    let output = ''
    if (href === '/vars') output = JSON.stringify(response['content'], null, 4)
    else if (href === '/log') output = response['content']

    return output
  }

  useInterval(
    () => {
      fetchAPI().then(setContent)
    }, 1000
  )

  return (
    <div className={classes.App}>
      <NavigationBar callback={setHref}/>
      <Content data={content}/>
    </div>
  )
}
