<template>
  <div id="app">
    <div class="container-fluid container-top-margin">
      <router-view/>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'app',

    mounted () {
      var usersnapKey = process.env.USERSNAP_KEY || null
      if (usersnapKey) {
        var s = document.createElement('script')
        s.type = 'text/javascript'
        s.async = true
        s.src = `//api.usersnap.com/load/${usersnapKey}.js`
        var x = document.getElementsByTagName('script')[0]
        x.parentNode.insertBefore(s, x)
      }
    }
  }
</script>

<style>
  #app {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .container-top-margin {
    margin-top: 4em;
  }
</style>
