import logo from '../../assets/icons/logo.png'

export default function Logo(props) {
  return (
    <div {...props}>
      <img src={logo} alt='logo'/>
      <span>NOSOK</span>
    </div>
  )
};
