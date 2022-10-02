import StatsChart from '../../../../components/StatsChart/StatsChart'

import classes from './Dashboard.module.scss'


export default function Dashboard() {
    return (
        <div class={classes.Dashboard}>
            <StatsChart id='memory' label='Memory usage, MB' area='memory'/>
            <StatsChart id='cpu' label='CPU usage, %' area='cpu'/>
        </div>
    )
}