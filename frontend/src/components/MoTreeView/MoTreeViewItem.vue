<template>
  <li class="item">
      <span @click="toggle">
        <icon class="icon" v-if="hasChildren" :name="open ? 'caret-down' : 'caret-right'"/>
      </span>
      <span class="icon" v-if="!hasChildren"/>

      <router-link 
        v-if="linkable"
        class="link-color" 
        :to="{ name: 'OrganisationDetail', params: { uuid: model.uuid } }"
      >
        <icon class="icon-color" name="users"/>
        {{model.name}}
      </router-link>

      <span 
        class="link-color"
        v-if="!linkable"
        @click="selectOrgUnit(model)"
      >
        <icon class="icon" name="users"/>
        {{model.name}}
      </span>

    <ul v-show="open">
      <mo-loader v-show="loading"/>
      <mo-tree-view-item
        v-for="(model, index) in model.children"
        :key="index"
        v-model="selected"
        :model="model"
        :at-date="atDate"
        :linkable="linkable"
      />
    </ul>
  </li>
</template>

<script>
  /**
   * A tree view item component
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoLoader from '@/components/atoms/MoLoader'

  export default {
    name: 'MoTreeViewItem',

    components: {
      MoLoader
    },

    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * Defines a model name.
       */
      model: Object,

      /**
       * This boolean property defines a open link.
       */
      firstOpen: Boolean,

      /**
       * This boolean defines a able link.
       */
      linkable: Boolean,

      /**
       * Defines a atDate.
       */
      atDate: [Date, String]
    },

    data () {
      return {
      /**
       * The selected, open, loading component value.
       * Used to detect changes and restore the value.
       */
        selected: {},
        open: false,
        loading: true
      }
    },

    computed: {
      /**
       * Show children if it has.
       */
      hasChildren () {
        return this.model.child_count > 0
      }
    },

    watch: {
      /**
       * When model change, load children.
       */
      model (val) {
        this.loadChildren()
      },

      /**
       * When selected change, update newVal.
       */
      selected (newVal) {
        this.selectOrgUnit(newVal)
      },

      /**
       * When atDate change, load children.
       */
      atDate () {
        this.loadChildren()
      }
    },

    mounted () {
      /**
       * Called after the instance has been mounted.
       * Set open as firstOpen.
       */
      if (this.firstOpen) {
        this.loadChildren()
      }
      this.open = this.firstOpen
    },

    methods: {
      /**
       * On toggle open children.
       */
      toggle () {
        this.open = !this.open
        if (this.open && this.model.children === undefined) this.loadChildren()
      },

      /**
       * When selectOrgUnit change, update org.
       */
      selectOrgUnit (org) {
        this.$emit('input', org)
      },

      /**
       * Get organisation unit children.
       */
      loadChildren () {
        let vm = this
        vm.loading = true
        vm.model.children = []
        OrganisationUnit.getChildren(vm.model.uuid, vm.atDate)
          .then(response => {
            vm.loading = false
            vm.model.children = response
          })
      }
    }
  }
</script>

<style scoped>
  ul {
    padding-left: 1.25rem;
  }

  .extra-padding {
    padding-left: 0.05rem;
  }

  .item {
    cursor: pointer;
    list-style-type: none;
    display: block;
    white-space: nowrap;
  }

  .nav-link {
    display: inline-block;
  }

  .icon {
    color: #343a40;
    width: 1rem;
    display: inline-block;
  }

  .link-color{
    color: #212529;
    text-decoration: none;
  }

  .link-color:hover{
    color: #007bff;
  }

  .router-link-active{
    color:#007bff;
  }
</style>
