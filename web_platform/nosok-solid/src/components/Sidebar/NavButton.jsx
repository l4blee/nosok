import classes from './NavButton.module.scss'

export default function NavButton({children, src, href, callback, alt}) {
  return (
    <button className={classes.NavButton} onClick={() => callback(href)}>
        <img src={src} alt={alt}/>
        <span>{children}</span>
    </button>
  )
}
