import Charts from '../../../components/ContentRelated/Charts'
import Log from '../../../components/ContentRelated/Log'

import classes from './Dashboard.module.scss'


export default function Dashboard() {
    return (
        <div class={classes.Dashboard}>
            <Charts/>
            <Log/>
        </div>
    )
}