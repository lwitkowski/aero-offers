<template>
  <multiselect
    v-model="selected"
    :options="available_aircraft_types"
    group-values="models"
    group-label="manufacturer"
    :group-select="false"
    :show-labels="false"
    label="model"
    :placeholder="'Search ' + (aircraft_type || 'aircraft')"
    :max-height="500"
  >
    <template #noResult>
      <span v-if="aircraft_type">
        {{ aircraft_type.charAt(0).toUpperCase() + aircraft_type.slice(1) }} not found. Try different phrase or
        category.
      </span>
      <span v-else>Aircraft model not found. Try different phrase.</span>
    </template>
  </multiselect>
</template>

<script>
import axios from 'axios'
import Multiselect from 'vue-multiselect'

export default {
  name: 'AircraftModelFilter',
  components: {
    Multiselect
  },
  props: {
    models: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      aircraft_type: null,
      all_aircraft_types: [],
      available_aircraft_types: [],
      selected: null
    }
  },

  watch: {
    $route() {
      this.parseAndApplyRoute()
    },

    selected(val) {
      if (val == null) {
        return
      }
      this.$router.push({
        name: 'model_details',
        params: { aircraftType: val.aircraft_type, manufacturer: val.manufacturer, model: val.model }
      })
    }
  },

  created() {
    this.loadAircraftTypes()
  },

  methods: {
    parseAndApplyRoute() {
      const pathSegments = this.$route.path.split('/')
      switch (pathSegments[1]) {
        case 'glider':
        case 'tmg':
        case 'ultralight':
        case 'airplane':
          this.aircraft_type = pathSegments[1]
          this.selected = null
          this.updateAircraftTypes()

          if (pathSegments.length == 4) {
            this.selected = {
              manufacturer: decodeURI(pathSegments[2]),
              model: decodeURI(pathSegments[3])
            }
          } else {
            this.selected = null
          }
          break

        default:
          this.aircraft_type = null
          this.selected = null
          this.updateAircraftTypes()
      }
    },
    loadAircraftTypes() {
      if (this.models) {
        this.all_aircraft_types = this.models

        this.parseAndApplyRoute()
        this.updateAircraftTypes()
        return
      }

      axios.get(`/api/models`).then((response) => {
        this.all_aircraft_types = response.data
        this.parseAndApplyRoute()
        this.updateAircraftTypes()
      })
    },

    updateAircraftTypes() {
      const new_available_aircraft_types = []
      for (const manufacturer in this.all_aircraft_types) {
        const modelsToDisplay = []

        const modelsByAircraftType = this.all_aircraft_types[manufacturer].models
        for (const type in modelsByAircraftType) {
          if (this.aircraft_type == type || this.aircraft_type == null) {
            for (const model in modelsByAircraftType[type]) {
              modelsToDisplay.push({
                aircraft_type: type,
                manufacturer: manufacturer,
                model: modelsByAircraftType[type][model]
              })
            }
          }
        }

        new_available_aircraft_types.push({
          manufacturer: manufacturer,
          models: modelsToDisplay
        })
      }

      this.available_aircraft_types = new_available_aircraft_types
    }
  }
}
</script>

<style lang="scss">
@import 'vue-multiselect/dist/vue-multiselect.css';
</style>
