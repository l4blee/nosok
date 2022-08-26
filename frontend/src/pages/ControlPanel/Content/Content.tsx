import classes from './Content.module.scss'
import Dashboard from './Dashboard/Dashboard'
import Log from './Logs/Log'

import { selectedButton } from '../../../global_ctx'

const [selected, _] = selectedButton


export default function Content() {
    return (
      <div class={classes.Content}>
        {
          selected() === 'dashboard' ?
          <Dashboard/> :
          <Log/>
        }
      </div>
    )
}