import React from 'react'
import classes from './Content.module.scss'

export default function Content({ children, ...props }) {
    return (
        <pre className={classes.Content}>
            {children}
        </pre>
    )
}
