<template>
  <div id="offers-content">
    <div id="explanation">
      aero-offers.com gathers data from various aircraft marketplaces and makes them available for insights.
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

export default {
  name: 'Offers',

  components: {
    OfferComponent
  },
  props: {
    filter: {
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
        .get(`/offers?${this.filter}&limit=${this.limit}&orderBy=creation_datetime&offset=${this.offset}`)
        .then((response) => {
          this.offers = this.offers.concat(response.data)
        })
      this.offset += this.limit
    }
  }
}
</script>

<style lang="css">
#explanation {
  box-shadow:
    0 2px 3px rgba(10, 10, 10, 0.1),
    0 0 0 1px rgba(10, 10, 10, 0.1);
  background-color: #ffffff;
  color: #373737;
}

#offers-div {
  padding: 10px;
}
</style>
