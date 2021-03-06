import Vue from 'vue'
import Vuex from 'vuex'
import auth from './modules/auth'
import employee from './modules/employee'
import log from './modules/log'
import organisation from './modules/organisation'
import organisationUnit from './modules/organisationUnit'
import employeeTerminate from './modules/employeeTerminate'
import employeeLeave from './modules/employeeLeave'
import facet from './modules/facet'

Vue.use(Vuex)

export default new Vuex.Store({
  // strict: true,
  modules: {
    auth: auth,
    employee: employee,
    log: log,
    organisation: organisation,
    organisationUnit: organisationUnit,
    employeeTerminate: employeeTerminate,
    employeeLeave: employeeLeave,
    facet: facet
  }
})
