var util = require('../../utils/util')
var wxCharts = require('../../utils/wxcharts.js')
const app = getApp()
var emojis = app.globalData.emojis
var columnChart = null;
var barChart = null;
var chartData = {
  main: {
    title: '总用电量',
    data: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    categories: ['E1-E2', 'E11', 'E12', 'E21', 'E32', 'N1-N2', 'N21', 'N23', 'N24', 'N6']
  },
};
Page({
  data: {
    messages: [],
    isSpeech: false,
    scrollHeight: 0,
    toView: '',
    windowHeight: 0,
    windowWidth: 0,
    pxToRpx: 2,
    msg: '',
    emotionBox: false,
    emotions: [],
    speechText: '按住 说话',
    changeImageUrl: '/images/voice.png',
    speechIcon: '/images/speech0.png',
    defaultSpeechIcon: '/images/speech0.png',
    emotionIcon: '/images/emotion.png',
    playingSpeech: '',
    code_w: 400,      //宽
    code_h: 200,        //高

    chartTitle: '总用电量 单位; m kwh',
    isMainChartDisplay: false
  },
  chooseEmotion(e) {
    this.setData({
      msg: this.data.msg + '[' + e.target.dataset.name + ']',
    })
  },
  sendMessage(e) {
    this.setData({
      msg: e.detail.value,
    })
  },
  onLoad() {
    var that = this
    let emotions = []
    for (let i = 0; i < emojis.length; i++) {
      emotions.push({
        src: '/emoji/' + util.getEmojiEn(emojis[i]) + '.png',
        id: i,
        name: emojis[i]
      })
    }
    this.setData({
      emotions: emotions
    })
    wx.getSystemInfo({
      success: (res) => {
        this.setData({
          windowHeight: res.windowHeight,
          pxToRpx: 750 / res.screenWidth,
          scrollHeight: res.windowHeight * 750 / res.screenWidth - 100
        })
      }
    })
    // this.charts()
  },
  onShareAppMessage: function () {
    return {
      title: 'UMor',
      path: '/pages/index/index'
    }
  },
  getMonitorDataBtn: function () {
    var that = this;
    wx.request({
      url: 'https://www.kenchan.net.cn:13011/total_ele',
      method: 'POST',
      data: {},
      header: {
        'Content-Type': 'application/json'
      },
      success: function (res) {
        if (res.statusCode == 200) {
          // console.log(res)
          // console.log(res.data)
          // console.log(res.data['E1-E2'])
          var answer = '';
          var i = 0;
          for (var key in res.data) {
            // console.log("key: " + key + " ,value: " + res.data[key]);
            answer = answer + key + '\t: ' + res.data[key] + '\n';
            chartData.main.data[i] = parseInt(res.data[key]) / 1000000;
            i = i + 1;
          }

          columnChart.updateData({
            categories: chartData.main.categories,
            series: [{
              name: '成交量',
              data: chartData.main.data,
              format: function (val, name) {
                return val.toFixed(2);
              }
            }]
          });
          
          that.setData({
            isMainChartDisplay: true
          })
        }
      },
      fail: function (res) {
        console.log(res)
      }
    })
  },

  backToMainChart: function () {
    this.setData({
      chartTitle: chartData.main.title,
      isMainChartDisplay: true
    });
    columnChart.updateData({
      categories: chartData.main.categories,
      series: [{
        name: '用电量',
        data: chartData.main.data,
        format: function (val, name) {
          return val.toFixed(2);
        }
      }]
    });
  },
 
  onReady: function (e) {
    // console.log("onReady!")
    var windowWidth = 320;
    try {
      var res = wx.getSystemInfoSync();
      windowWidth = res.windowWidth;
    } catch (e) {
      console.error('getSystemInfoSync failed!');
    }

    columnChart = new wxCharts({
      canvasId: 'columnCanvas',
      type: 'column',
      animation: true,
      categories: chartData.main.categories,
      series: [{
        name: '用电量',
        data: chartData.main.data,
        format: function (val, name) {
          return val.toFixed(2);
        }
      }],
      yAxis: {
        format: function (val) {
          return val ;
        },
        //title: 'hello',
        min: 0
      },
      xAxis: {
        disableGrid: true,
      
      },
      
      extra: {
        column: {
          width: 10
        }
      },
      width: windowWidth,
      height: 180,
    });
  }


  
})
