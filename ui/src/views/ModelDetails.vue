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
      <div id="chart" class="ct-chart">
        <Chart :data="chartData" :options="chartOptions" />
      </div>
      <h2>Offers</h2>
      <p>
        There were {{ offers.length }} offer(s). Median offer price is
        <span class="median_price">{{ formatPrice(medianPrice, 'EUR') }},</span>
        average {{ formatPrice(avgPrice, 'EUR') }}.
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
        <tbody>
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
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import regression from 'regression'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  TimeScale
} from 'chart.js'
import { Chart } from 'vue-chartjs'
import 'chartjs-adapter-date-fns'

import { formatPrice, median } from '@/utils.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, TimeScale)

export default {
  name: 'ModelDetails',

  components: {
    Chart
  },
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
        datasets: []
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            parsing: false,
            time: {
              displayFormats: {
                quarter: 'MMM YYYY'
              }
            }
          }
        },
        plugins: {
          tooltip: {
            filter: function (tooltipItem) {
              return tooltipItem.datasetIndex === 0
            },
            callbacks: {
              label: function (context) {
                return [context.raw.offer.title, formatPrice(context.parsed.y, 'EUR')]
              }
            }
          }
        }
      }
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
    formatPrice,

    fetchData() {
      this.chartData.datasets = []
      this.avgPrice = 0
      this.medianPrice = 0

      axios.get(`/api/offers/${this.manufacturer}/${this.model}`).then((response) => {
        this.manufacturer_website = response.data.manufacturer_website
        this.offers = response.data.offers
        if (this.offers.length === 0) {
          return
        }

        this.offers.sort((a, b) => new Date(a.published_at) - new Date(b.published_at))

        let points = []
        let prices = []
        let priceSum = 0
        const dataPointsForRegression = []
        for (let i = 0; i < this.offers.length; i += 1) {
          const offer = this.offers[i]
          if (!isNaN(offer.price.amount_in_euro)) {
            let price = Number(offer.price.amount_in_euro)
            prices.push(price)
            priceSum += price
          }

          const datapoint = {
            x: new Date(offer.published_at),
            y: Number(offer.price.amount_in_euro),
            offer: offer
          }
          points.push(datapoint)
          dataPointsForRegression.push([
            datapoint.x.getTime() / 100000, // this is needed for regression calculations to work correctly
            datapoint.y
          ])
        }

        let datasets = [
          {
            label: 'Offers',
            type: 'scatter',
            backgroundColor: '#f87979',
            borderColor: '#f87979',
            pointRadius: 5,
            data: points
          }
        ]

        let regressionLine = this.drawLinearRegressionLine(dataPointsForRegression)
        if (regressionLine) {
          datasets.push(regressionLine)
        }
        this.chartData = { datasets: datasets }

        this.avgPrice = Math.round((priceSum / this.offers.length) * 100) / 100
        this.medianPrice = median(prices)
      })
    },

    drawLinearRegressionLine(dataPoints) {
      const regressionResult = regression.linear(dataPoints)
      if (regressionResult.points.length < 2) {
        return null
      }
      const startPoint = regressionResult.points[0]
      const endPoint = regressionResult.points[regressionResult.points.length - 1]

      return {
        label: 'regression',
        type: 'line',
        borderColor: '#4281ec66',
        pointStyle: false,
        borderWidth: 5,
        data: [
          { x: new Date(startPoint[0] * 100000), y: startPoint[1] },
          { x: new Date(endPoint[0] * 100000), y: endPoint[1] }
        ]
      }
    }
  }
}
</script>

<style lang="scss">
#chart {
  margin: auto;
  padding: 20px;
  height: 600px;
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
