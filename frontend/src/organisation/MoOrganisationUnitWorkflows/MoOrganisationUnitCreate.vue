<template>
  <b-modal 
    id="orgUnitCreate" 
    size="lg" 
    :title="$t('workflows.organisation.create_unit')"
    ref="orgUnitCreate"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="createOrganisationUnit">
      <mo-organisation-unit-entry
        v-model="entry"
        :creating-date="true"
      />

      <h5 class="mt-3">{{$tc('workflows.employee.labels.address', 2)}}</h5>
      <mo-address-entry 
        class="mt-3" 
        v-model="postAddress" 
        preselected-type="AdressePost" 
        validity-hidden required
      />

      <mo-address-entry 
        class="mt-3" 
        v-model="phone" 
        preselected-type="Telefon" 
        validity-hidden 
        required
      />

      <mo-add-many
        class="mt-3"
        :entry-component="addressEntry"
        :label="$tc('workflows.employee.labels.other_addresses')"
        v-model="addresses"
        validity-hidden
      />

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
  /**
   * A organisation unit create component
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoOrganisationUnitEntry from '@/components/MoEntry/MoOrganisationUnitEntry'
  import MoAddMany from '@/components/MoAddMany/MoAddMany'
  import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

  export default {
      /**
       * Requesting a new validator scope to its children
       */
    $_veeValidate: {
      validator: 'new'
    },

    name: 'OrganisationUnitCreate',

    components: {
      ButtonSubmit,
      MoOrganisationUnitEntry,
      MoAddressEntry,
      MoAddMany
    },

    data () {
      return {
        /**
         * The entry, postAddress, phone, addresses, isLoading, backendValidationError component value.
         * Used to detect changes and restore the value.
         */
        entry: {
          validity: {}
        },
        addresses: [],
        postAddress: {},
        phone: {},
        isLoading: false,
        backendValidationError: null,

        /**
         * The addressEntry component.
         * Used to add MoAddressEntry component in `<mo-add-many/>`.
         */
        addressEntry: MoAddressEntry
      }
    },

    computed: {
      /**
       * Loop over all contents of the fields object and check if they exist and valid.
       */
      formValid () {
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },

    methods: {
      /**
       * Resets the data fields.
       */
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },

      /**
       * Create a organisation unit and check if the data fields are valid.
       * Then throw a error if not.
       */
      createOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          this.isLoading = true

          this.addresses.push(this.postAddress, this.phone)
          this.entry.addresses = this.addresses

          OrganisationUnit.create(this.entry)
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.orgUnitCreate.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
