<template>
  <div class="row">
    <div class="col-12 workflow-padding">
      <router-view :key="$route.params.uuid"/>

      <mo-log/>
    </div>
    
    <mo-employee-workflows/>
  </div>
</template>

<script>
  /**
   * A employee component.
   */

  import MoEmployeeWorkflows from './MoEmployeeWorkflows/MoEmployeeWorkflows'
  import MoLog from '@/components/MoLog/MoLog'

  export default {
    components: {
      MoEmployeeWorkflows,
      MoLog
    }
  }
</script>

<style scoped>
  @media (min-width: 768px) {
   .workflow-padding {
    padding-right: 75px;
    }
   }

   @media (max-width: 768px) {
   .workflow-padding {
    padding-top: 30px;
    }
  }
</style>
