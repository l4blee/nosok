import classes from './NavButton.module.scss'

import { selectedButton } from '../../global_ctx'

const [nav, setNav] = selectedButton

interface Props {
  children: string, 
  src: string, 
  navigate: string
  alt: string
}

export default function NavButton({
    children, 
    src, 
    navigate,
    alt
  }: Props){
    return (
      <button class={`${classes.NavButton} ${Boolean(navigate === nav()) ? classes.NavButtonSelected : ''}`}
              onClick={() => setNav(navigate)}>
        <img src={src} alt={alt}/>
        <span>{children}</span>
      </button>
    )
}