import React from 'react'
import classes from './Content.module.css'

export default function Content({data}) {    
    return (
        <div className={classes.Content}>
            <pre>
                {data}
            </pre>
        </div>
    )
}
