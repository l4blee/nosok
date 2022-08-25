import { Accessor, createSignal, Setter } from "solid-js"

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

const [nav, setNav] = createSignal('dashboard')

const auth: [Accessor<boolean>, () => void] = [isAuth, updAuth]
const sid: [Accessor<string | undefined>, Setter<string>] = [sID, setSID]
const selectedButton: [Accessor<string>, Setter<string>] = [nav, setNav]

export {auth, sid, selectedButton}
