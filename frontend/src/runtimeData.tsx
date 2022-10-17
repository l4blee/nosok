import { createStore } from "solid-js/store"

import { io } from 'socket.io-client'

type VarsBlock = {cpu_used: number, memory_used: number}
type VarsPayload = {status: string, servers: number, vars: VarsBlock}

type RuntimeData = {status: string, servers: number, vars: VarsBlock}
type RuntimeStatsStorage = {log: string, overview: RuntimeData}

type PollingPayload = {changed: string, content: string | VarsPayload}
type APIPayload = {message: string, content: string | VarsPayload}


const socket = io('')
const [data, setData] = createStore<RuntimeStatsStorage>({
    log: '',
    overview: {
        status: 'offline',
        servers: 0,
        vars: {
            cpu_used: 0, 
            memory_used: 0
        }
    }
})

async function fetchAPI(href: string): Promise<string | VarsPayload> {
    return fetch('/api' + href)
           .then(res => res.json())
           .then((payload: APIPayload) => payload.content)
           .catch(_ => {
               return href === '/log' ?
                      '' :
                      {
                           status: 'unknown',
                           servers: 0,
                           vars: {
                               cpu_used: 0,
                               memory_used: 0
                           }
                      }
           })
}

async function refreshLog() {
    await fetchAPI('/log').then(log => {
        setData({
            log: log as string,
        })  
    })
}

async function refreshVars() {
    await fetchAPI('/vars').then(vars => {
        vars = vars as VarsPayload            

        setData({
            overview: {
                status: vars.status,
                servers: vars.servers,
                vars: vars.vars
            }
        })
    })
}

async function refreshData() {
    await refreshLog()
    await refreshVars()
}

function onWSPayload(payload: PollingPayload) {
    if (payload.changed === 'log') {
        setData({
            ...data,
            log: payload.content as string
        })
    } else if (payload.changed === 'variables') {
        const payloadData = payload.content as VarsPayload
    
        setData({
            ...data,
            overview: {
                status: payloadData.status,
                servers: payloadData.servers,
                vars: payloadData.vars
            }
        })
    }
}
socket.on('data_changed', onWSPayload)

export {socket, data, refreshData, refreshLog, refreshVars}
export type { VarsBlock }