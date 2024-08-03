import { AuthStore } from "./stores/main";
import API_URL from "./constants";
import router from "./router/index.js"
async function fetchData(path) {
    var store = AuthStore()

    const response = await fetch(API_URL+path, {
        headers: {
            'Authorization': `Bearer ${store.authToken}`
        }
    })

    // check if response code is 200
    if (!response.ok) {
        //logout and redirect to /error
        store.logout()
        router.push({ name: 'error' })
    }
    return await response.json()
}

export default fetchData