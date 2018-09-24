import axios from 'axios'
import store from '@/vuex/store'
import {AUTH_REQUEST} from '@/vuex/actions/auth'

/**
 * Defines the base url and headers for http calls
 */

const Service = axios.create({
  baseURL: '/service',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})

export default {
  get (url) {
    return Service
      .get(url)
      .catch(err => {
        console.warn('request failed', err)

        if (err.response.status === 401) {
          return store.dispatch(AUTH_REQUEST)
        }

        if (err.response.status === 403) {
          //TODO: Do a thing
        }

        return new Promise(function (resolve, reject) {
          reject(err)
        })
      })
  },

  post (url, payload) {
    return Service
      .post(url, payload)
  }
}
