const { defineConfig } = require('@vue/cli-service')
const {gitDescribe, gitDescribeSync} = require('git-describe');

process.env.VUE_APP_GIT_HASH = gitDescribeSync().hash
process.env.VUE_APP_BUILD_TIMESTAMP = new Date().toISOString()

module.exports = defineConfig({
  devServer: {
      port: 8082,
  },
  lintOnSave: false
})
