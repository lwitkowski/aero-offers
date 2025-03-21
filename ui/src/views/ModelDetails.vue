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
      <p>
        There were {{ offers.length }} offer(s). Median offer price is
        <span class="median_price">{{ formatPrice(medianPrice, 'EUR') }}</span>
        , average {{ formatPrice(avgPrice, 'EUR') }}.
      </p>
      <table class="modelinformation-table">
        <tr>
          <th>Date</th>
          <th>Title</th>
          <th>Location</th>
          <th>Hours / starts</th>
          <th>Price</th>
          <th />
        </tr>
        <tr v-for="offer in offers.slice().reverse()" :key="offer.id">
          <td>{{ offer.published_at }}</td>
          <td>{{ offer.title }}</td>
          <td>{{ offer.location }}</td>
          <td>
            <div v-if="offer.hours">{{ offer.hours }}h, {{ offer.starts }} starts</div>
            <div v-else>n/a</div>
          </td>
          <td>{{ formatPrice(offer.price.amount, offer.price.currency) }}</td>
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
import regression from 'regression'
import ChartistTooltip from 'chartist-plugin-tooltips-updated'
import { formatPrice, median } from '@/utils.js'

export default {
  name: 'ModelDetails',

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
      avgPrice: 0,
      medianPrice: 0,
      chartData: {
        series: [[], []]
      },
      chartOptions: {
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
    formatPrice,
    dateAlreadyPresent(date) {
      for (let j = 0; j < this.chartData.series[0].length; j++) {
        if (moment(this.chartData.series[0][j].x).isSame(date, 'day')) {
          return true
        }
      }
      return false
    },

    drawLinearRegressionLine(dataPoints) {
      const regressionResult = regression.linear(dataPoints)
      if (regressionResult.points.length >= 2) {
        const startPoint = regressionResult.points[0]
        const endPoint = regressionResult.points[regressionResult.points.length - 1]
        this.chartData.series[1] = [
          { x: new Date(startPoint[0] * 100000), y: startPoint[1] },
          { x: new Date(endPoint[0] * 100000), y: endPoint[1] }
        ]
      } else {
        this.chartData.series[1] = []
      }
    },

    fetchData() {
      this.chartData.series = [[]]
      this.avgPrice = 0

      axios.get(`/api/offers/${this.manufacturer}/${this.model}`).then((response) => {
        this.manufacturer_website = response.data.manufacturer_website
        this.offers = response.data.offers
        this.offers.sort((a, b) => new Date(a.published_at) - new Date(b.published_at))

        if (this.offers.length === 0) {
          return
        }

        let prices = []
        const dataPointsForRegression = []
        for (let i = 0; i < this.offers.length; i += 1) {
          const offer = this.offers[i]
          if (!isNaN(offer.price.amount_in_euro)) {
            prices.push(Number(offer.price.amount_in_euro))
          }

          const datapoint = {
            meta: offer.title,
            x: new Date(offer.published_at),
            y: Number(offer.price.amount_in_euro)
          }
          if (this.dateAlreadyPresent(datapoint.x)) {
            this.chartData.series.push([datapoint])
            continue
          }
          this.chartData.series[0].push(datapoint)
          dataPointsForRegression.push([
            datapoint.x.getTime() / 100000, // this is needed for regression calculations to work correctly
            datapoint.y
          ])
        }
        this.chartOptions = {
          showLine: true,
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
                return formatPrice(datapoint.split(',')[1], 'EUR')
              }
            })
          ]
        }

        this.drawLinearRegressionLine(dataPointsForRegression)

        let priceSum = 0
        prices.forEach((num) => {
          priceSum += num
        })
        this.avgPrice = Math.round((priceSum / this.offers.length) * 100) / 100
        this.medianPrice = median(prices)
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

.ct-series-a .ct-line {
  stroke-width: 0px;
}
.ct-series-a .ct-point {
  stroke: #df3a26;
  stroke-width: 10px;
}

.ct-series-b .ct-line {
  stroke: #4281ec66;
  stroke-width: 5px;
}
.ct-series-b .ct-point {
  stroke-width: 0px;
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

.median_price {
  color: #ee6c4d;
  font-weight: bold;
}
</style>
