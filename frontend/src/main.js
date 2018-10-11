// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import App from './App'
import router from './router'
import VueI18n from 'vue-i18n'
import { da } from './i18n/da'
import VeeValidate, { Validator } from 'vee-validate'
import DateInRange from './validators/DateInRange'
import messagesDA from '../node_modules/vee-validate/dist/locale/da'
import VueShortKey from 'vue-shortkey'
import store from './vuex/store'

import 'vue-awesome/icons'
import Icon from 'vue-awesome/components/Icon'

require('../node_modules/bootstrap/dist/css/bootstrap.css')
require('../node_modules/bootstrap-vue/dist/bootstrap-vue')
require('./assets/css/global.css')
require('../node_modules/vue-dawa/dist/vue-dawa.min.css')

const moment = require('moment')
require('moment/locale/da')

Vue.config.productionTip = false

const veeConfig = {
  dateFormat: 'DD-MM-YYYY',
  delay: 100,
  locale: 'da',
  inject: false
}

Validator.localize('da', messagesDA)

Validator.extend('date_in_range', DateInRange)

Vue.use(BootstrapVue)
Vue.use(VueI18n)
Vue.use(VeeValidate, veeConfig)
Vue.use(require('vue-moment'), {
  moment
})
Vue.use(VueShortKey, { prevent: ['input', 'textarea'] })
Vue.component('icon', Icon)

const messages = {
  da: da
}

const i18n = new VueI18n({
  locale: 'da', // set locale
  messages
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  i18n,
  router,
  store,
  template: '<App/>',
  components: { App }
})
