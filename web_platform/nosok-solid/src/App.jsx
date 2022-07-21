import { createSignal, onCleanup, onMount } from 'solid-js'

import Sidebar from './components/Sidebar/Sidebar'
import Header from './components/Header/Header'
import Content from './components/Content'
import { io } from 'socket.io-client'
import classes from './App.module.css'


async function fetchAPI(href) {
  if (href === '') return ''  // just in case

  return await fetch('/api' + href)
               .then(res => res.json())
               .then(data => data.content)
               .catch(_ => {return ''})
}

function prepareContent(ctn) {
  switch (href) {
    case '/vars':
      return JSON.stringify(ctn, null, 4)

    case '/log':
      return ctn

    default:
      return '';
  }
}

const socket = io('')
var href = '/log'

export default function App() {
  const [content, setContent] = createSignal('')
  const onDataChange = (payload) => {if (payload.href === href) setContent(prepareContent(payload.content))}
  
  onMount(() => {
    fetchAPI(href).then(prepareContent).then(setContent)

    socket.on(
      'data_changed', 
      onDataChange
    )
  })

  onCleanup(() => {
    socket.off(
      'data_changed',
      onDataChange
    )
    socket.disconnect()
  })

  return (
    <div className={classes.App}>
      <Header/>
      <Sidebar callback={(newHref) => {href = newHref; fetchAPI(newHref).then(prepareContent).then(setContent)}}/>
      <Content>{content}</Content>
    </div>
  )
}
