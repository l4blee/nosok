import classes from './NavButton.module.scss'

import { link } from '../../global_ctx'

const [global_href, _] = link

export default function NavButton({children, src, href, callback, alt}) {
  return (
    <button className={`${classes.NavButton} ${Boolean(href === global_href()) ? classes.NavButtonSelected : ''}`} onClick={() => callback(href)}>
      <img src={src} alt={alt}/>
      <span>{children}</span>
    </button>
  )
}