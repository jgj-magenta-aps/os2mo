<template>
  <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-primary">
    <router-link class="logo col-1" :to="{ name: 'Landing'}"></router-link>

    <button 
      class="navbar-toggler" 
      type="button" 
      data-toggle="collapse" 
      data-target="#navbarSupportedContent" 
      aria-controls="navbarSupportedContent"
      aria-expanded="false" 
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'Employee'}">{{$t('navbar.employee')}}</router-link>
        </li>

        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'Organisation'}">{{$t('navbar.organisation')}}</router-link>
        </li>
      </ul>

      <mo-organisation-picker reset-route class="ml-auto mr-auto"/>

      <mo-search-bar class="ml-auto mr-auto"/>

      <router-link :to="{ name: 'QueryList'}">
        <button type="button" aria-label="Foresørgsler" class="btn btn-link text-white">
          <icon name="exchange-alt"/>
        </button>
      </router-link>

      <mo-time-machine-button/>

      <help-button/>

      <b-dropdown id="ddown1" variant="primary">
        <template slot="button-content">
          <icon name="user"/> {{username}}
        </template>

        <b-dropdown-item @click="logout()">
          <icon name="sign-out-alt"/> Log ud
        </b-dropdown-item>
      </b-dropdown>
    </div>
  </nav>
</template>

<script>
  import {AUTH_LOGOUT} from '@/store/actions/auth'
  import HelpButton from '@/help/TheHelpButton'
  import MoTimeMachineButton from '@/timeMachine/MoTimeMachineButton'
  import MoSearchBar from './MoSearchBar/MoSearchBar'
  import MoOrganisationPicker from '@/components/MoPicker/MoOrganisationPicker'
  import Service from '@/api/HttpCommon'

  export default {
    components: {
      HelpButton,
      MoTimeMachineButton,
      MoSearchBar,
      MoOrganisationPicker
    },

    data () {
      return {
        user: {},
        username: 'N/A'
      }
    },

    created () {
      /**
       * Called synchronously after the instance is created.
       * Get user and then response data.
       */
      Service.get('/user').then(response => {
        this.username = response.data || 'N/A'
      })
    },

    methods: {
      /**
       * Get the logout and redirect.
       */
      logout () {
        let vm = this
        this.$store.dispatch(AUTH_LOGOUT, vm.user)
      }
    }
  }
</script>

<style lang="scss" scoped>
  .logo {
    background-image: url('../assets/logo/os2_small.svg');
    background-repeat: no-repeat; /*Prevent showing multiple background images*/
    background-position: center;
    background-color:#002f5d;
    background-size: 60px;
    width: 60px;
    height: 50px;
    margin-left: -1em;
  }

  nav {
    height: 50px;
  }

  .nav-item {
    .nav-link {
      font-family: Oswald,Arial,sans-serif !important;
      color: #e5e0de !important;

      &:hover {
        border-bottom: 3px solid #e5e0de;
      }
    }

    .router-link-active {
      border-bottom: 3px solid #e5e0de;
    }
  }
</style>
