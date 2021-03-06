
import { AUTH_LOGOUT, AUTH_REQUEST, AUTH_SUCCESS, AUTH_ERROR } from '../actions/auth'

const state = {
  accessToken: sessionStorage.getItem('access_token') || '',
  username: null,
  status: ''
}

const mutations = {
  [AUTH_LOGOUT] (state) {
    state.accessToken = ''
    state.username = ''
  },

  [AUTH_SUCCESS]: (state, data) => {
    state.accessToken = data.token
    state.username = data.username
    state.status = ''
  },

  [AUTH_ERROR]: (state, key) => {
    state.status = key
  }
}

const actions = {
  [AUTH_REQUEST]: ({commit}, user) => {
    window.location.href = '/saml/sso/?next=' + window.location
  },

  [AUTH_LOGOUT]: ({commit}, user) => {
    window.location.href = '/saml/slo/'
  }
}

const getters = {
  username: state => state.username,
  status: state => state.status,
  isAuthenticated: state => !!state.accessToken,
  accessToken: state => state.accessToken
}

export default {
  state,
  mutations,
  actions,
  getters
}
