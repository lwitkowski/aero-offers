<template>
  <div id="offers-content">
    <div id="offers-div">
      <OfferThumb v-for="offer in offers" :key="offer.id" :offer="offer" />
      <button class="click-button" @click="fetchData">Load more Offers</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import OfferThumb from '../components/OfferThumb.vue'

export default {
  name: 'OffersList',

  components: {
    OfferThumb
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
      limit: 30
    }
  },

  created() {
    this.fetchData()
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
    }
  }
}
</script>

<style lang="css">
#offers-div {
  padding: 10px;
}
</style>
