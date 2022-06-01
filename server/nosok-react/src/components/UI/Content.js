import React from 'react'
import classes from './Content.module.css'

export default function Content({data}) {
    return (
        <pre className={classes.Content}>
            {data}
        </pre>
    )
}
