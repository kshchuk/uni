import Keycloak from 'keycloak-js';
import {setToken} from "./Config";

let initOptions = {
    url: 'http://localhost:1488/',
    realm: 'LabRealm',
    clientId: 'react-client',
}

let kc = new Keycloak(initOptions);

kc.init({
    onLoad: 'login-required',
    checkLoginIframe: true,
    pkceMethod: 'S256'
}).then((auth) => {
    if (!auth) {
        window.location.reload();
    } else {
        console.info("Authenticated");
        setToken('Bearer ' + kc.token)
    }
}, () => {
    console.error("Authentication Failed");
});

export default kc;

