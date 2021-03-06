<template>
  <b-modal 
    id="employeeMove" 
    size="lg" 
    :title="$t('workflows.employee.move_engagement')"
    ref="employeeMove"
    hide-footer 
    lazy
    no-close-on-backdrop
    @hidden="resetData"
  >
    <form @submit.stop.prevent="moveEmployee">
      <mo-employee-picker 
        class="search-employee" 
        v-model="move.data.person" 
        required
      />

      <div class="form-row">
        <mo-engagement-picker 
          class="mt-3" 
          v-model="original" 
          :employee="move.data.person"
          required
        />
      </div>

      <div class="form-row">
        <mo-organisation-unit-picker
          :label="$t('input_fields.move_to')" 
          class="col" 
          v-model="move.data.org_unit"
          required
        />       
      </div>

      <div class="form-row">
        <mo-date-picker 
          class="col from-date"
          :label="$t('input_fields.move_date')" 
          v-model="move.data.validity.from"
          :valid-dates="validDates"
          required
        />
      </div>

      <mo-confirm-checkbox
        :entry-date="move.data.validity.from"
        :entry-name="original.engagement_type.name"
        :entry-org-name="original.org_unit.name"
        v-if="dateConflict" 
        required
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
   * A employee move component.
   */

  import Employee from '@/api/Employee'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoEngagementPicker from '@/components/MoPicker/MoEngagementPicker'
  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoConfirmCheckbox from '@/components/MoConfirmCheckbox'

  export default {
      /**
       * Requesting a new validator scope to its children.
       */
    $_veeValidate: {
      validator: 'new'
    },

    components: {
      MoDatePicker,
      MoOrganisationUnitPicker,
      MoEngagementPicker,
      MoEmployeePicker,
      ButtonSubmit,
      MoConfirmCheckbox
    },

    props: {
      /**
       * Defines a engagement type name.
       */
      entryName: String,

      /**
       * Defines a from date.
       */
      entryDate: Date,

      /**
       * Defines a orgName.
       */
      entryOrgName: String
    },

    data () {
      return {
      /**
        * The move, original, isLoading, backendValidationError component value.
        * Used to detect changes and restore the value.
        */
        isLoading: false,
        backendValidationError: null,
        original: null,
        move: {
          type: 'engagement',
          person: {},
          data: {
            validity: {}
          }
        }
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
      },

      /**
       * Check if the dates are valid.
       */
      dateConflict () {
        if (this.move.data.validity.from && this.original) {
          if (this.original.validity.to == null) return true
          this.move.data.validity.from = new Date(this.move.data.validity.from)
          this.original.validity.to = new Date(this.original.validity.to)
          if (this.move.data.validity.from <= this.original.validity.to) return true
        }
        return false
      },

      /**
       * Check if the organisation date are valid.
       */
      validDates () {
        return this.move.data.org_unit ? this.move.data.org_unit.validity : {}
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
       * Move a employee and check if the data fields are valid.
       * Then throw a error if not.
       */
      moveEmployee (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true
          vm.move.uuid = this.original.uuid

          Employee.move([this.move])
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.employeeMove.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
