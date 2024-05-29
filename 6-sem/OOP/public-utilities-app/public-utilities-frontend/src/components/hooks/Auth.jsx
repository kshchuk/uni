import Keycloak from 'keycloak-js';
import {setToken} from "./Config";

let initOptions = {
    url: 'http://localhost:1488/',
    realm: 'labs-realm',
    clientId: 'public-utilities-client',
}

let kc = new Keycloak(initOptions);

let auth = await kc.init({
    onLoad: 'login-required',
    checkLoginIframe: true,
})

if (!auth) {
    window.location.reload();
} else {
    console.info("Authenticated");
}

export {kc};