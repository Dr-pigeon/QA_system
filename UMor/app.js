App({
  globalData: {
    host: 'https://www.kenchan.net.cn:13011/applet',
    emojisEn: ['bugaoxing', 'guai', 'qinqin', 'lengmo', 'qie', 'mianqiang', 'chijing', 'tushe', 'hehe', 'hu', 'yi', 'haha', 'ku', 'pen', 'weiqu', 'kaixin', 'deyi', 'nu', 'exin', 'jingku', 'jingya', 'han', 'huaji', 'kuanghan', 'shengqi', 'yiwen', 'zhenbang', 'shuijue', 'xiaoyan', 'mengmengda', 'bishi', 'yinxian', 'heixian'],
    emojis: ['不高兴', '乖', '亲亲', '冷漠', '切~', '勉强', '吃惊', '吐舌', '呵呵', '呼~', '咦', '哈哈', '哭', '喷', '委屈', '开心', '得意', '怒', '恶心', '惊哭', '惊讶', '汗', '滑稽', '狂汗', '生气', '疑问', '真棒', '睡觉', '笑眼', '萌萌哒', '鄙视', '阴险', '黑线']
  },
  onLaunch: function () {
    var that = this;
    wx.getSetting({
      success(res) {
        if (!res['scope.record']) {
          wx.authorize({
            scope: 'scope.record'
          })
        }
        if (!res['scope.userInfo']) {
          wx.authorize({
            scope: 'scope.userInfo'
          })
        }
      }
    })
    // wx.login({
    //   success: function (data) {
    //     wx.getUserInfo({
    //       success: function (res) {
    //         wx.setStorage({
    //           key: 'userInfo',
    //           data: res.userInfo,
    //         })
    //       }
    //     })
    //     wx.request({
    //       method: 'POST',
    //       url: that.globalData.host,
    //       data: {
    //         'action':'login',
    //         'code': data.code,
    //         'type':'userinfo'
    //       },
    //       header: {
    //         'Content-Type': 'application/json'
    //       },
    //       success: function (res) {
    //         wx.setStorage({
    //           key: "f55b1d19d23f21442a488b6f9b28ea42",
    //           "userid": "fool",
    //           "info": res.data,
    //         })
    //       }
    //     });
    //   }
    // })
  }
})

