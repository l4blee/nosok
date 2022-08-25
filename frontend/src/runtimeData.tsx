import { createStore } from "solid-js/store"

import { io } from 'socket.io-client'

import type { RuntimeStatsStorage, PollingPayload, VarsPayload, APIPayload } from "./interfaces"

const socket = io('')
const [data, setData] = createStore<RuntimeStatsStorage>({
    log: '',
    overview: {
        status: 'offline',
        servers: 0,
        vars: []
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

async function refreshData() {
    await fetchAPI('/log').then(log => {
        setData({
            log: log as string,
        })  
    })

    await fetchAPI('/vars').then(vars => {
        vars = vars as VarsPayload            

        setData({
            overview: {
                status: vars.status,
                servers: vars.servers,
                vars: [vars.vars]
            }
        })
    })
}

function onWSPayload(payload: PollingPayload) {
    if (payload.changed === 'log') {
        setData({
            ...data,
            log: payload.content as string
        })
    } else if (payload.changed === 'variables') {
        const payloadData = payload.content as VarsPayload
    
        var varsArray = [...data.overview.vars, payloadData.vars]
        if(varsArray.length > 10) varsArray = varsArray.slice(1, 11)
    
        setData({
            ...data,
            overview: {
                status: payloadData.status,
                servers: payloadData.servers,
                vars: varsArray
            }
        })
    }
}
socket.on('data_changed', onWSPayload)

export {socket, data, refreshData}