<template>
  <div class="offer-div">
    <div class="description">
      <p>
        <strong>{{ offer.title }}</strong>
      </p>
      <p>
        <small>{{ offer.date }}, {{ offer.location }}</small>
        ,
        <small
          ><strong
            >{{ offer.price_in_euro }}
            <div v-if="offer.currency_code != 'EUR'" class="tooltip">
              <span class="tooltiptext"> converted from {{ offer.price }} {{ offer.currency }}</span
              >€
            </div>
            <div v-else style="display: inline">€</div>
          </strong></small
        >
      </p>
      <small
        ><p v-if="offer.manufacturer">
          <router-link
            :to="{
              name: 'ModelInformation',
              params: { manufacturer: this.offer.manufacturer, model: this.offer.model }
            }"
          >
            <a>Model: {{ offer.manufacturer }} {{ offer.model }}</a></router-link
          >
        </p></small
      >
    </div>
    <div class="icon">
      <small
        ><a v-bind:href="offer.url" target="_blank">
          <img :src="'url_icon.png'" alt="Link to Offer" height="30" width="30" /></a
      ></small>
    </div>
  </div>
</template>

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
    color: #ee6c4d;
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

<script>
export default {
  name: 'OfferComponent',
  props: ['offer']
}
</script>
