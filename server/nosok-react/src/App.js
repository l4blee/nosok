import React, { useState } from 'react'
import NavigationBar from './components/UI/NavigationBar/NavigationBar'
import Content from './components/UI/Content'

import classes from './App.module.css'

export default function App() {
  const [content, setContent] = useState()

  function updateContent(data) {
    setContent(data)
  }

  return (
    <div className={classes.App}>
      <NavigationBar callback={updateContent}/>
      <Content data={content}/>
    </div>
  )
}
