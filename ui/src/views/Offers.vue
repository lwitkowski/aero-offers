<template>
  <div id="offers-content">
    <div id="aircraft-type-filter">
      <multiselect
        v-model="selected"
        :options="available_aircraft_types"
        group-values="models"
        group-label="manufacturer"
        :group-select="false"
        label="model"
        :placeholder="'Filter ' + (aircraft_type ? aircraft_type + ' ' : 'aircraft ') + 'type'"
      >
        <template #noResult>
          <span>Oops! Aircraft type not found. Try different phrase.</span>
        </template>
      </multiselect>
    </div>

    <div id="offers-div">
      <OfferComponent v-for="offer in offers" :key="offer.id" :offer="offer" />
      <button class="click-button" @click="fetchData">Load more Offers</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import OfferComponent from '../components/OfferComponent.vue'
import Multiselect from 'vue-multiselect'

export default {
  name: 'Offers',

  components: {
    OfferComponent,
    Multiselect
  },
  props: {
    aircraftType: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      offers: [],
      offset: 0,
      limit: 30,

      available_aircraft_types: [],
      selected: ''
    }
  },

  watch: {
    selected(val) {
      if (val !== null) {
        this.$router.push({
          name: 'ModelInformation',
          params: { manufacturer: val.manufacturer, model: val.model }
        })
      }
    }
  },

  created() {
    this.fetchData()
    this.fetchAircraftTypes()
  },

  methods: {
    fetchData() {
      axios
        .get(`/offers`, {
          params: {
            aircraft_type: this.aircraftType,
            limit: this.limit,
            offset: this.offset
          }
        })
        .then((response) => {
          this.offers = this.offers.concat(response.data)
        })
      this.offset += this.limit
    },
    fetchAircraftTypes() {
      axios.get(`/models`).then((response) => {
        this.available_aircraft_types = []
        for (const manufacturer in response.data) {
          const modelsToDisplay = []

          const modelsByAircraftType = response.data[manufacturer].models
          for (const type in modelsByAircraftType) {
            if (this.aircraft_type == type || this.aircraft_type == null) {
              for (const model in modelsByAircraftType[type]) {
                modelsToDisplay.push({
                  manufacturer: manufacturer,
                  model: modelsByAircraftType[type][model]
                })
              }
            }
          }

          this.available_aircraft_types.push({
            manufacturer: manufacturer,
            models: modelsToDisplay
          })
        }
      })
    }
  }
}
</script>

<style lang="css">
@import 'vue-multiselect/dist/vue-multiselect.css';

#offers-div {
  padding: 10px;
}

#aircraft-type-filter {
  padding: 5px;
  width: 400px;
}
</style>
