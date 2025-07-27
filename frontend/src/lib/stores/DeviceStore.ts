import createCookiePersistentStore from "$lib/utils/store/createCookiePersistentStore";
import { stringCodec } from "$lib/utils/store/storeCodecs";

export const DEVICE_TOKEN = 'unisync-device';
const {
    store: DeviceStore, set: setDevice
} = createCookiePersistentStore<Device>({
    tokenName: DEVICE_TOKEN,

    encode(data) {
        return data as string;
    },

    decode(raw) {
        return raw as Device;
    }
});

export { DeviceStore, setDevice }