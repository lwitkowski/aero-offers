<template>
  <div id="modelinformation">
    <div v-if="offers">
      <h1>{{ manufacturer }} {{ model }}</h1>
      <h2>Manufacturer Info</h2>
      <p v-if="manufacturer_website">
        Website:
        <a :href="manufacturer_website" target="_blank">{{ manufacturer_website }}</a>
      </p>
      <h2>Price Chart</h2>
      <div id="chart">
        <chartist type="Line" ratio=".ct-chart" :data="chartData" :options="chartOptions" />
      </div>
      <h2>Offers</h2>
      <p>There were {{ offers.length }} offer(s) for this Model. The average offer price is {{ medianPrice }} Euro.</p>
      <table class="modelinformation-table">
        <tr>
          <th>Date</th>
          <th>Title</th>
          <th>Location</th>
          <th>Price</th>
          <th />
        </tr>
        <tr v-for="offer in offers.slice().reverse()" :key="offer.id">
          <td>{{ offer.date }}</td>
          <td>{{ offer.title }}</td>
          <td>{{ offer.location }}</td>
          <td>{{ offer.price_in_euro }} €</td>
          <td>
            <div class="icon">
              <small>
                <a :href="offer.url" target="_blank">
                  <img :src="'../../url_icon.png'" alt="Link to Offer" height="30" width="30" />
                </a>
              </small>
            </div>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import ChartistTooltip from 'chartist-plugin-tooltips-updated'

export default {
  name: 'ModelInformation',

  components: {},
  props: {
    manufacturer: {
      type: String,
      default: null
    },
    model: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      manufacturer_website: '',
      offers: [],
      medianPrice: 0,
      chartData: {
        series: [[]]
      },
      chartOptions: {
        low: 0,
        width: 600,
        height: 600,
        showArea: false,
        plugins: [
          ChartistTooltip({
            class: 'tooltip'
          })
        ]
      }
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
    dateAlreadyPresent(date) {
      for (let j = 0; j < this.chartData.series[0].length; j++) {
        if (moment(this.chartData.series[0][j].x).isSame(date, 'day')) {
          return true
        }
      }
      return false
    },

    fetchData() {
      this.chartData.series = [[]]
      axios.get(`/model/${this.manufacturer}/${this.model}`).then((response) => {
        this.manufacturer_website = response.data.manufacturer_website
        this.offers = response.data.offers
        if (this.offers.length === 0) {
          return
        }

        for (let i = 0; i < this.offers.length; i += 1) {
          const offer = this.offers[i]
          this.medianPrice += offer.price_in_euro

          const datapoint = {
            meta: offer.title,
            x: new Date(offer.date),
            y: offer.price_in_euro
          }
          if (this.dateAlreadyPresent(datapoint.x)) {
            this.chartData.series.push([datapoint])
            continue
          }
          this.chartData.series[0].push(datapoint)
        }
        this.chartOptions = {
          axisX: {
            type: this.$chartist.FixedScaleAxis,
            divisor: 6,
            labelInterpolationFnc: function (value) {
              return moment(value).format('MMM-DD-YYYY')
            }
          },
          width: 600,
          height: 600,
          low: 0,
          plugins: [
            this.$chartist.plugins.tooltip({
              transformTooltipTextFnc: (datapoint) => {
                return datapoint.split(',')[1] + ' €'
              }
            })
          ]
        }
        this.medianPrice = Math.round((this.medianPrice / this.offers.length) * 100) / 100
      })
    }
  }
}
</script>

<style lang="scss">
@import 'chartist/dist/scss/chartist.scss';
@import 'chartist-plugin-tooltips-updated/dist/chartist-plugin-tooltip.scss';

#chart {
  margin: auto;
  width: 600px;
  height: 600px;
}

.chartist-tooltip::before {
  border-top-color: #011627;
}

.chartist-tooltip {
  color: #ffffff;
  font-weight: 100;
  background-color: #011627;
}

.modelinformation-table {
  text-align: left;
  margin: auto;
}

.modelinformation-table th {
  text-align: center;
  background-color: #011627;
  color: #ffffff;
}
</style>
