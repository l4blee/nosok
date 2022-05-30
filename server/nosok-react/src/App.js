import React, { useState } from 'react'
import NavigationBar from './components/UI/NavigationBar/NavigationBar'
import Content from './components/UI/Content'
import DataContext from './components/UI/DataContext'

import classes from './App.module.css'

export default function App() {
  const [content, setContent] = useState('default')

  return (
    <div className={classes.App}>
      <DataContext.Provider value={[content, setContent]}>
        <NavigationBar/>
        <Content/>
      </DataContext.Provider>
    </div>
  )
}
