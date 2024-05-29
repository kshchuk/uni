import {useContext} from "react";
import AuthContext from "../context/AuthProvider";

const getHeaderConfig = () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const auth = useContext(AuthContext);

    return {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + auth.token,
        }
    };
}

export default getHeaderConfig;
