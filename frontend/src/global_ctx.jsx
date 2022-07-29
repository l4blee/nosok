import { createSignal } from "solid-js"

const [sID, setSID] = createSignal(
    document.cookie
    .split('; ')
    .find((row) => row.startsWith('session='))
    ?.split('=')[1]
)
const [isAuth, setAuth] = createSignal(Boolean(sID()))

function updAuth() {
    let sessionID = document.cookie
                .split('; ')
                .find((row) => row.startsWith('session='))
                ?.split('=')[1]
    
    setSID(sessionID)
    setAuth(Boolean(sessionID))
}

updAuth()

const [href, setHref] = createSignal('/log')

const auth = [isAuth, updAuth]
const sid = [sID, setSID]
const link = [href, setHref]

export {auth, sid, link}
