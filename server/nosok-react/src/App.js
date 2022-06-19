import React, { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar/Sidebar'
import Header from './components/Header/Header'
import Content from './components/Content'
import { io } from 'socket.io-client'
import classes from './App.module.css'


async function fetchAPI(href) {
  if (href === '') return ''
  let response = await fetch('/api' + href)
                       .then(res => res.json())
                       .catch(e => {return ''})
  
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
  
  useEffect(() => {
    let onDataChange = (payload) => {if (payload.href === href) updContent(payload.content)}

    fetchAPI(href).then(updContent)
    socket.on('data_changed', onDataChange)
    
    return () => {
      socket.off('data_changed', onDataChange)
    }
  }, [])

  return (
    <div className={classes.App}>
      <Header/>
      <Sidebar callback={(newHref) => {href = newHref; fetchAPI(newHref).then(updContent)}}/>
      <Content>{content}</Content>
    </div>
  )
}
