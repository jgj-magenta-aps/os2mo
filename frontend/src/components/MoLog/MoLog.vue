<template>
  <div class="card card-margin">
    <div class="card-body">
      <h5>{{label}}</h5>
      <mo-worklog/>
    </div>
  </div>
</template>

<script>
  /**
   * A log component.
   */

  import MoWorklog from './MoWorklog'
  import MoErrors from './MoErrors'

  export default {
    name: 'MoLog',

    components: {
      MoWorklog,
      MoErrors
    },

    data () {
      return {
      /**
        * The label component value.
        * Used to set a default value.
        */
        label: 'Arbejdslog'
      }
    }
  }
</script>

<style scoped>
  .card-margin {
    margin-top: 2em;
    min-height: 150px;
  }
</style>
