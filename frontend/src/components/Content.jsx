import classes from './Content.module.scss'

export default function Content({ children }) {
    return (
        <pre className={classes.Content}>
            {children}
        </pre>
    )
}
