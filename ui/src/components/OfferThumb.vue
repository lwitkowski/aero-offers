<template>
  <div class="offer-div">
    <div class="description">
      <p>
        <strong>{{ offer.title }}</strong>
      </p>
      <p>
        <small>{{ offer.date }}, {{ offer.location }}</small>
        ,
        <small>
          <strong>{{ formatPrice(offer.price.amount, offer.price.currency_code) }}</strong>
        </small>
      </p>
      <small>
        <p v-if="offer.hours">Total: {{ offer.hours }}h, {{ offer.starts }} starts</p>
      </small>
      <small>
        <p v-if="offer.manufacturer">
          <router-link
            :to="{
              name: 'model_details',
              params: { aircraftType: offer.aircraft_type, manufacturer: offer.manufacturer, model: offer.model }
            }"
          >
            <a>all `{{ offer.model }}` offers</a>
          </router-link>
        </p>
      </small>
    </div>
    <div class="icon">
      <small>
        <a :href="offer.url" target="_blank">
          <img :src="'/url_icon.png'" alt="Link to Offer" height="30" width="30" />
        </a>
      </small>
    </div>
  </div>
</template>

<script>
import { formatPrice } from '@/utils.js'

export default {
  name: 'OfferThumb',
  props: {
    offer: {
      type: Object,
      default: null
    }
  },
  methods: {
    formatPrice
  }
}
</script>

<style lang="css">
.icon {
  display: table-cell;
  box-sizing: border-box;
  vertical-align: middle;
  width: 50px;
  margin-right: 15px;
}

.description {
  display: table-cell;
  box-sizing: border-box;
  small {
    font-size: 12px;
    color: #cc6c4d;
  }
}

.offer-div {
  float: left;
  margin: 5px;
  padding: 5px;
  display: table;
  width: 350px;
  background-color: #ffffff;
  color: #373737;
  box-shadow:
    0 2px 3px rgba(10, 10, 10, 0.1),
    0 0 0 1px rgba(10, 10, 10, 0.1);
  + .offer-div {
    margin-top: 10px;
  }
}
</style>
