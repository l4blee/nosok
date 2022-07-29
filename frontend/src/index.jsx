/* @refresh reload */
import { render } from 'solid-js/web';
import { Router } from '@solidjs/router'

import 'bootstrap/dist/css/bootstrap.min.css'
import './index.scss';
import App from './App';

render(
    () => (
        <Router>
            <App/>
        </Router>        
    ), 
    document.getElementById('root')
);
