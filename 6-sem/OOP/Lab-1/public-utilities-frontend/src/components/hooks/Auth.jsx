import Keycloak from 'keycloak-js';
import {setToken} from "./Config";

let initOptions = {
    url: 'http://localhost:1488/',
    realm: 'LabRealm',
    clientId: 'react-client',
}

let kc = new Keycloak(initOptions);

let auth = await kc.init({
    onLoad: 'login-required',
    checkLoginIframe: true,
    pkceMethod: 'S256'
})

if (!auth) {
    window.location.reload();
} else {
    console.info("Authenticated");
    setToken('Bearer ' + kc.token)
}

export default kc;

