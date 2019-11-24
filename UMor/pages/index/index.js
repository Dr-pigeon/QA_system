var util = require('../../utils/util')
const app = getApp()
var emojis = app.globalData.emojis
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
    monitorIcon: '/images/crosshair-png-aim-1-original.png',
    playingSpeech: '',
    settingFlag: 0,
    targetUsage: 0
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
    this.settingFlag = 0;
    this.targetUsage = 0;
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
          // scrollHeight: (res.windowHeight - 80) * 750 / res.screenWidth
          scrollHeight: res.windowHeight * 750 / res.screenWidth - 200
        })
      }
    })
  },
  onShareAppMessage: function () {
    return {
      title: 'UMor',
      path: '/pages/index/index'
    }
  },
  monitorBtn: function() {
    wx.navigateTo({
      url: '../monitor/monitor'
    })
  },
  emotionBtn() {
    if (this.data.emotionBox) {
      this.setData({
        emotionBox: false,
        scrollHeight: this.data.windowHeight * this.data.pxToRpx - 200  
      })
    } else {
      this.setData({
        emotionBox: true,
        scrollHeight: this.data.windowHeight * this.data.pxToRpx - 650  
      })
      if (this.data.isSpeech) {
        this.setData({
          isSpeech: false,
          changeImageUrl: '/images/voice.png'
        });
      }
    }
  }, 
  changeType: function () {
    if (this.data.isSpeech) {
      this.setData({
        isSpeech: false,
        changeImageUrl: '/images/voice.png'
      });
    } else {
      this.setData({
        isSpeech: true,
        changeImageUrl: '/images/keyinput.png',
        emotionBox: false,
        scrollHeight: this.data.windowHeight * this.data.pxToRpx - 200
      });
    }
  },
  send: function () {
    var that = this;
    let msg = this.data.msg;
    let contents = util.getContents(msg);
    console.log(contents);
    let fake_input_record = msg;
    let id = 'id_' + Date.parse(new Date()) / 1000;
    let data = { id: id, contents: contents, me: true, avatar: wx.getStorageSync('userInfo').avatarUrl, speech: false }
    let messages = this.data.messages
    messages.push(data)
    this.setData({
      messages: messages,
      msg: ''
    })
    this.setData({
      toView: id
    })

    if (this.settingFlag == 1){
      this.targetUsage = parseFloat(data.contents[0]['text'])
      console.log(this.targetUsage);
    }
    
    // console.log(this.settingFlag)
    if (this.settingFlag == 0){
      wx.request({
        url: 'https://www.kenchan.net.cn:13011/applet',
        method: 'POST',
        data: { "text": data.contents[0]['text'], 'action': 'text' },
        success: function (res) {
          if (res.statusCode == 200) {
            console.log(res);
            if (res.data.type == 'text') {
              console.log(res.data)
              // console.log(）
              let answer = res.data.text;
              let contents = util.getContents(answer)
              let id = 'id_' + Date.parse(new Date()) / 1000;
              let data = { id: id, contents: contents, me: false, avatar: '/images/robot.jpg', speech: false }
              let messages = that.data.messages;
              messages.push(data)
              // console.log(messages)
              that.setData({
                messages: messages
              })
              that.setData({
                toView: id
              })
            } else if (res.data.type == 'img') {
              wx.request({
                url: 'https://www.kenchan.net.cn:13011/img',
                method: 'POST',
                responseType: 'arraybuffer',
                success: function (res) {
                  if (res.statusCode == 200) {
                    console.log(res);
                    let base64 = wx.arrayBufferToBase64(res.data)
                    base64 = 'data:image/jpeg;base64, ' + base64;
                    let contents = util.getContents('None', base64, 1);
                    let id = 'id_' + Date.parse(new Date()) / 1000;
                    let data = { id: id, contents: contents, me: false, avatar: '/images/robot.jpg', speech: false }
                    messages.push(data)
                    // console.log(messages)
                    that.setData({
                      messages: messages
                    })
                    that.setData({
                      toView: id
                    })
                  }
                }
              })
            }
          }
        },
        fail: function (res) {
          console.log(res)
        }
      })

    } else if (this.settingFlag == 1){
      // console.log(data.contents[0]['text'])
      wx.request({
        url: 'https://www.kenchan.net.cn:13011/usage',
        method: 'POST',
        data: { "value": data.contents[0]['text'], "type": "setting" }, 
        header: {
          'Content-Type': 'application/json'
        },
        success: function (res) {
          if (res.statusCode == 200) {
            console.log(res);
            let answer = res.data; 
            let contents = util.getContents(answer)
            let id = 'id_' + Date.parse(new Date()) / 1000;
            let data = { id: id, contents: contents, me: false, avatar: '/images/robot.jpg', speech: false }
            let messages = that.data.messages;
            messages.push(data)
            // console.log(messages)
            that.setData({
              messages: messages
            })
            that.setData({
              toView: id
            })


          }
        },
        fail: function (res) {
          console.log(res)
        }
      })
      this.settingFlag = 0;
    } 
  },
  setTargetUsage: function () {
    var that = this;
    let msg = "我想设定本月总电力消耗目标用量";
    let contents = util.getContents(msg);
    console.log(contents);
    let id = 'id_' + Date.parse(new Date()) / 1000;
    let data = { id: id, contents: contents, me: true, avatar: wx.getStorageSync('userInfo').avatarUrl, speech: false }
    let messages = this.data.messages
    messages.push(data)
    this.setData({
      messages: messages,
      msg: ''
    })
    this.setData({
      toView: id
    })
    
    setTimeout(function () {
      let msg = "请输入一般用量";
      let contents = util.getContents(msg);
      console.log(contents);
      let id = 'id_' + Date.parse(new Date()) / 1000;
      let data = { id: id, contents: contents, me: false, avatar: '/images/robot.jpg', speech: false }
      let messages = that.data.messages
      messages.push(data)
      that.setData({
        messages: messages,
        msg: ''
      })
      that.setData({
        toView: id
      })
    }, 500);

    this.settingFlag = 1;
  },
  getUsageAlarm: function () {
    var that = this;
    wx.request({
      url: 'https://www.kenchan.net.cn:13011/usage',
      method: 'POST',
      data: { "type": "recog" },
      header: {
        'Content-Type': 'application/json'
      },
      success: function (res) {
        if (res.statusCode == 200) {
          console.log(res);
          let answer = res.data;
          let contents = util.getContents(answer)
          let id = 'id_' + Date.parse(new Date()) / 1000;
          let data = { id: id, contents: contents, me: false, avatar: '/images/robot.jpg', speech: false }
          let messages = that.data.messages;
          messages.push(data)
          // console.log(messages)
          that.setData({
            messages: messages
          })
          that.setData({
            toView: id
          })
        }
      },
      fail: function (res) {
        console.log(res)
      }
    })
  },
  startRecord: function () {
    var that = this;
    this.setData({
      speechText: '松开 发送'
    })
    var seconds = 0;
    var interval = setInterval(function () {
      seconds++
    }, 1000);
    wx.startRecord({
      success: function (res) {
        clearInterval(interval);
        var tempFilePath = res.tempFilePath
        seconds = seconds == 0 ? 1 : seconds;
        let id = 'id_' + Date.parse(new Date()) / 1000;
        let data = { id: id, me: true, avatar: wx.getStorageSync('userInfo').avatarUrl, speech: true, seconds: seconds, filePath: tempFilePath }
        let messages = that.data.messages
        messages.push(data)
        that.setData({
          messages: messages
        });
        that.setData({
          toView: id
        })
        let nickName = wx.getStorageSync('userInfo').nickName;
        if (!nickName) nickName = 'null';
        wx.uploadFile({
          url:'http://www.kenchan.net.cn:13011/applet',
          filePath: tempFilePath,
          name: 'voice',
          formData: {
            'action': 'voice',
            'userid': wx.getStorageSync('openid'),
            'username': wx.getStorageSync('userInfo').nickName
          },
          success: function (res) {
            let resData = JSON.parse(res.data);
            if (resData.code == 102) {
              let answer = resData.text;
              let contents = util.getContents(answer)
              let id = 'id_' + Date.parse(new Date()) / 1000;
              let data = { id: id, contents: contents, me: false, avatar: '/images/robot.jpg', speech: false }
              let messages = that.data.messages
              messages.push(data)
              that.setData({
                messages: messages
              })
              that.setData({
                toView: id
              })
            } else if (resData.code == 101) {
              var isFirst = true;
              wx.playBackgroundAudio({
                dataUrl: host + '/static/' + resData.text
              });
              wx.onBackgroundAudioPlay(function () {
                wx.getBackgroundAudioPlayerState({
                  success: function (res) {
                    if (!isFirst) {
                      return;
                    }
                    isFirst = false;
                    let duration = res.duration;
                    wx.stopBackgroundAudio();
                    let id = 'id_' + Date.parse(new Date()) / 1000;
                    let data = { id: id, me: false, avatar: '/images/robot.jpg', speech: true, seconds: duration == 0 ? 1 : duration, filePath: host + '/static/' + resData.text }
                    let messages = that.data.messages
                    messages.push(data)
                    that.setData({
                      messages: messages
                    });
                    that.setData({
                      toView: id
                    })
                  }
                })
              });
            }
          },
          fail: function (err) {
            console.log(err)
          }
        })
      },
      fail: function (err) {
        console.log(err)
      }
    })
  },
  stopRecord: function () {
    this.setData({
      speechText: '按住 说话'
    })
    wx.stopRecord();
  },
  playSpeech: function (event) {
    var that = this;
    var filePath = event.currentTarget.dataset.filepath;
    that.setData({
      playingSpeech: filePath
    });
    var num = 1;
    var interval = setInterval(function () {
      that.setData({
        speechIcon: '/images/speech' + num % 3 + '.png'
      });
      num++;
    }, 500);
    wx.playVoice({
      filePath: filePath,
      complete: function () {
        clearInterval(interval);
        that.setData({
          speechIcon: '/images/speech0.png',
          playingSpeech: ''
        });
      }
    })
  },
  playRobotSpeech: function (event) {
    var that = this;
    var filePath = event.currentTarget.dataset.filepath;
    that.setData({
      playingSpeech: filePath
    });
    var num = 1;
    var interval = setInterval(function () {
      that.setData({
        speechIcon: '/images/speech' + num % 3 + '.png'
      });
      num++;
    }, 500);
    wx.playBackgroundAudio({
      dataUrl: filePath
    });
    wx.onBackgroundAudioStop(function () {
      clearInterval(interval);
      that.setData({
        speechIcon: '/images/speech0.png',
        playingSpeech: ''
      });
    })
  }
})

// ['E11在11月17日用电', 1, 'text']
// ['E11在11月17日8点到10点用电', 1, 'text']
// ['E11在11月17日和11月16日哪天用电多', 2, 'text']
// ['E11和E12在11月10日哪里用电多', 2, 'text']
// ['E11在11月17日用电趋势', 3, 'img']
// ['E11在11月17日上午8点到下午3点用电趋势', 3, 'img']
// ['E11在12月5日的用电预测', 4, 'text']
// ['E11在12月1日到12月10日的用电预测', 4, 'text']
// ['E11在11月28日上午6点到下午3点的用电预测', 4, 'text']
// ['E12在11月30日下午5点的用电预测', 4, 'text']