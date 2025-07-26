import createCookiePersistentStore from "$lib/utils/store/createCookiePersistentStore";
import { stringCodec } from "$lib/utils/store/storeCodecs";

export const JWT_TOKEN_NAME = 'unisync-jwt-token';
const {
    store: JwtTokenStore, set: setJwtToken
} = createCookiePersistentStore<string>({
    tokenName: JWT_TOKEN_NAME,
    ...stringCodec,
});

export { JwtTokenStore, setJwtToken };