import { ref, computed } from 'vue'
import { defineStore } from 'pinia'


const defaultAuth = () => ({
  authToken: "",
  loggedIn: false,
  userInfo: {}
})
const getSettings = () => {
  const auth = localStorage.getItem("AuthStore")
  return auth ? JSON.parse(auth) : defaultAuth()
}

export const AuthStore = defineStore('auth', {
  state: () => {
    return getSettings()
  },
  actions: {
    login(authToken, userInfo) {
      this.authToken = authToken
      this.loggedIn = true
      this.userInfo = userInfo
      localStorage.setItem("AuthStore", JSON.stringify(this.$state))
    },
    logout() {
      this.authToken = ""
      this.loggedIn = false
      this.userInfo = {}
      localStorage.setItem("AuthStore", JSON.stringify(this.$state))
    }
  },
})