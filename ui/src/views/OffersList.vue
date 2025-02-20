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
    category: {
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
        .get(`/api/offers`, {
          params: {
            category: this.category,
            limit: this.limit,
            offset: this.offset
          }
        })
        .then((response) => {
          this.offers = this.offers.concat(response.data)
          this.offset += this.limit
        })
    }
  }
}
</script>

<style lang="css">
#offers-div {
  padding: 10px;
}

.click-button {
  background-color: #011627;
  color: #ffffff;
  width: 40%;
  height: 40px;
  display: block;
  clear: left;
  border-radius: 2px;
  padding: 10px;
  margin: 0 auto;
  font-size: 14px;
}
</style>
