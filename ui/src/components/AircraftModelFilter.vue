<template>
  <multiselect
    v-model="selected"
    :options="available_aircraft_categories"
    group-values="models"
    group-label="manufacturer"
    :group-select="false"
    :show-labels="false"
    label="model"
    :placeholder="'Search ' + (category || 'aircraft')"
    :max-height="500"
  >
    <template #noResult>
      <span v-if="category">
        {{ category.charAt(0).toUpperCase() + category.slice(1) }} not found. Try different phrase or category.
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
      category: null,
      all_aircraft_categories: [],
      available_aircraft_categories: [],
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
        params: { category: val.category, manufacturer: val.manufacturer, model: val.model }
      })
    }
  },

  created() {
    this.loadAircraftCategories()
  },

  methods: {
    parseAndApplyRoute() {
      const pathSegments = this.$route.path.split('/')
      switch (pathSegments[1]) {
        case 'glider':
        case 'tmg':
        case 'ultralight':
        case 'airplane':
          this.category = pathSegments[1]
          this.selected = null
          this.updateAircraftCategories()

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
          this.category = null
          this.selected = null
          this.updateAircraftCategories()
      }
    },
    loadAircraftCategories() {
      if (this.models) {
        this.all_aircraft_categories = this.models

        this.parseAndApplyRoute()
        this.updateAircraftCategories()
        return
      }

      axios.get(`/api/models`).then((response) => {
        this.all_aircraft_categories = response.data
        this.parseAndApplyRoute()
        this.updateAircraftCategories()
      })
    },

    updateAircraftCategories() {
      const new_available_aircraft_categories = []
      for (const manufacturer in this.all_aircraft_categories) {
        const modelsToDisplay = []

        const modelsByAircraftCategory = this.all_aircraft_categories[manufacturer].models
        for (const category in modelsByAircraftCategory) {
          if (this.category == category || this.category == null) {
            for (const model in modelsByAircraftCategory[category]) {
              modelsToDisplay.push({
                category: category,
                manufacturer: manufacturer,
                model: modelsByAircraftCategory[category][model]
              })
            }
          }
        }

        new_available_aircraft_categories.push({
          manufacturer: manufacturer,
          models: modelsToDisplay
        })
      }

      this.available_aircraft_categories = new_available_aircraft_categories
    }
  }
}
</script>

<style lang="scss">
@import 'vue-multiselect/dist/vue-multiselect.css';
</style>
