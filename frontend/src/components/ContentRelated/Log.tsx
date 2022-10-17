import { data, refreshLog } from '../../runtimeData'
import classes from './Log.module.scss'


export default function Log() {
    refreshLog()
    
    return (
        <div class={classes.Log}>
            <pre>{data.log}</pre>
        </div>
    )
}