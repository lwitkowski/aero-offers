<template>
  <div id="offers-content">
    <div id="explanation">
      aero-offers.com gathers data from various aircraft marketplaces and makes them available for insights.
    </div>
    <div id="offers-div">
      <OfferComponent v-for="offer in offers" :offer="offer" v-bind:key="offer.id" />
      <button class="click-button" v-on:click="fetchData">Load more Offers</button>
    </div>
  </div>
</template>

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

<script>
import HTTP from '../http-common'
import OfferComponent from '../components/OfferComponent.vue'

export default {
  name: 'Offers',
  props: ['filter'],
  data() {
    return {
      offers: [],
      offset: 0,
      limit: 30
    }
  },

  methods: {
    fetchData() {
      HTTP.get(`/offers?${this.filter}&limit=${this.limit}&orderBy=creation_datetime&offset=${this.offset}`).then(
        (response) => {
          this.offers = this.offers.concat(response.data)
        }
      )
      this.offset += this.limit
    }
  },

  components: {
    OfferComponent
  },

  created() {
    this.fetchData()
  }
}
</script>
