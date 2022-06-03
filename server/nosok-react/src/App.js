import React, { useEffect, useState } from 'react'
import NavigationBar from './components/UI/NavigationBar/NavigationBar'
import Content from './components/UI/Content'
import { io } from 'socket.io-client'
import classes from './App.module.css'


async function fetchAPI(href) {
  if (href === '') return ''
  let response = await fetch('/api' + href)
  .then(res => res.json())
  
  if (response === undefined) return ''
  return response['content']
}

const socket = io('')
var href = '/log'

export default function App() {
  const [content, setContent] = useState('')

  const updContent = (ctn) => {
    switch (href) {
      case '/vars':
        setContent(JSON.stringify(ctn, null, 4))
        break;

      case '/log':
        setContent(ctn)
        break;

      default:
        break;
    }
  }

  function onDataChange(payload) {
    const reqHref = payload.href
    if (reqHref === href) {
      updContent(payload.content)
    }
  }
  
  useEffect(() => {
    fetchAPI(href).then(updContent)

    socket.on('log_changed', onDataChange)
    socket.on('vars_changed', onDataChange)
    
    return () => {
      socket.off('log_changed', onDataChange)
      socket.off('vars_changed', onDataChange)
    }
  }, [])

  function setHref(newHref) {
    href = newHref
    fetchAPI(href).then(updContent)
  }

  return (
    <div className={classes.App}>
      <NavigationBar callback={setHref}/>
      <Content>{content}</Content>
    </div>
  )
}
