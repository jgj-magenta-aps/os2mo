<template>
  <div>
    <div class="form-row">
      <mo-address-search-field class="mb-0" v-model="address" :label="label" :global="global"/>
      
      <label class="form-check-label">
        <input class="form-check-input" type="checkbox" v-model="global"/> 
        Søg i hele landet
      </label>
    </div>
  </div>
</template>

<script>
  /**
   * A address search component.
   */

  import MoAddressSearchField from './MoAddressSearchField'

  export default {
    components: {
      MoAddressSearchField
    },

    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * Defines a label.
       */
      label: String
    },

    data () {
      return {
      /**
        * The address, global component value.
        * Used to detect changes and restore the value.
        */
        address: {},
        global: false
      }
    },

    watch: {
      /**
       * Whenever address change update val.
       */
      address (val) {
        this.$emit('input', val)
      }
    },

    created () {
      /**
       * Called synchronously after the instance is created.
       * Set address to value.
       */
      this.address = this.value
    }
  }
</script>
