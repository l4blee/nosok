import React from 'react'

export default function NavButton({children, src, className, href, callback}) {
  return (
    <button className={className} onClick={() => callback(href)}>
        <img src={src} alt={className}/>
        <span>{children}</span>
    </button>
  )
}
