import StatsChart from '../StatsChart/StatsChart'
import { refreshVars } from '../../runtimeData'

import classes from './Charts.module.scss'

export default function Charts() {
    refreshVars()

    return (
        <div class={classes.Charts}>
            <StatsChart id='memory' label='Memory usage'/>
            <StatsChart id='cpu' label='CPU usage'/>
        </div>
    )
}