import React, { useContext } from 'react'
import classes from './Content.module.css'
import DataContext from './DataContext'

export default function Content() {
    const [data,] = useContext(DataContext)
    
    return (
        <div className={classes.Content}>
            <div dangerouslySetInnerHTML={{'__html': data['data']}}>
            </div>
        </div>
    )
}
