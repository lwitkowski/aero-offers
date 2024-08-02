<template>
  <div id="app">
    <div class="header">
      <div id="logo">
        <img src="/logo_v3.png" width="300" height="109" />
      </div>
      <div id="nav">
        <div class="nav-element">
          <router-link to="/">All Offers</router-link>
        </div>
        <div class="nav-element">
          <router-link to="/glider">Gliders</router-link>
        </div>
        <div class="nav-element">
          <router-link to="/tmg">TMG</router-link>
        </div>
        <div class="nav-element">
          <router-link to="/ultralight">Ultralight</router-link>
        </div>
        <div class="nav-element">
          <router-link to="/airplane">Airplanes</router-link>
        </div>
      </div>

      <div id="aircraft-type-filter">
        <AircraftModelFilter />
      </div>
    </div>
    <div id="body">
      <router-view :key="$route.path" />
    </div>
    <div id="footer">
      {{ buildInfo }}
    </div>
  </div>
</template>

<script>
/*global __COMMIT_HASH__*/
/*global __BUILD_TIMESTAMP__*/

import AircraftModelFilter from './components/AircraftModelFilter.vue'

export default {
  components: {
    AircraftModelFilter
  },
  data() {
    return {
      buildInfo: 'Build: ' + __COMMIT_HASH__ + ', ' + __BUILD_TIMESTAMP__
    }
  }
}
</script>

<style lang="scss">
* {
  box-sizing: border-box;
  margin: 0px;
}

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}

.header {
  display: grid;
  grid-template-columns: 10fr 1fr 1fr;
  grid-template-rows: auto auto;
  padding: 10px;
  background-color: #011627;
  width: 100%;
}

/* mobile version */
.header {
  display: grid;
  grid-template-columns: auto auto;
  grid-template-rows: auto auto auto;
}

#logo {
  grid-column: 1 / span 2;
  grid-row: 1;
}

#nav {
  grid-column: 1 / span 2;
  grid-row: 2;
}

.style-chooser {
  grid-column: 1;
  grid-row: 3;
}

.feedback-component {
  grid-column: 1;
  grid-row: 3;
}

/* desktop version */
@media all and (min-width: 500px) {
  .header {
    display: grid;
    grid-template-columns: 1fr auto auto;
    grid-template-rows: auto auto;
  }

  #logo {
    grid-column: 1 / span 3;
    grid-row: 1;
  }

  #nav {
    grid-column: 1;
    grid-row: 2;
  }

  .style-chooser {
    grid-column: 2;
    grid-row: 2;
  }

  .feedback-component {
    margin-left: 10px;
    grid-column: 3;
    grid-row: 2;
  }
}

#nav {
  font-size: 16px;
}

.style-chooser {
  width: 300px;
  margin: auto;
  background-color: #ffffff;
}

.nav-element {
  display: block;
  float: left;
  padding: 10px;
  background-color: #011627;
  font-size: 20 px;
  font-weight: bold;
  border-radius: 2px;
  margin-left: 10px;
}

#nav a {
  font-weight: bold;
  color: #ffffff;
}

#nav a.router-link-active {
  color: #f71735;
  text-decoration: none;
}

#body {
  background: #fdfffc;
  margin-bottom: 10px;
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

.close-button {
  background-color: #f71735;
  float: right;
  width: 25px;
  height: 25px;
  margin: 10px;
}

#footer a {
  text-decoration: none;
  font-size: 14px;
  color: #000000;
}

#footer {
  width: 350px;
  margin: auto;
  background-color: #ffffff;
  color: #373737;
}

.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 0;
  position: absolute;
  z-index: 1;
  bottom: 150%;
  left: 50%;
  margin-left: -60px;
}

.tooltip .tooltiptext::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: black transparent transparent transparent;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}

#aircraft-type-filter {
  padding: 5px;
  width: 500px;
}
</style>
