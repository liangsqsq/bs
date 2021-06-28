function initEcharts(divId, name, time, key, historyType, limit, auth) {
    var url = 'http://192.168.12.243/zabbix/api_jsonrpc.php';
    // auth = '541374ddb8b6c66b9e911f0b2f8e0440';
    var myChart = echarts.init(document.getElementById(divId));
// 显示标题，图例和空的坐标轴
    myChart.setOption({
        title: {
            text: 'CPU',
            left: '50%',
            textAlign: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                lineStyle: {
                    color: '#ddd'
                }
            },
            backgroundColor: 'rgba(255,255,255,1)',
            padding: [5, 10],
            textStyle: {
                color: '#7588E4'
            },
            extraCssText: 'box-shadow: 0 0 5px rgba(0,0,0,0.3)'
        },
        legend: {
            right: 20,
            orient: 'vertical',
            data: 'cpu'
        },
        xAxis: {
            type: 'category',
            data: [],
            boundaryGap: false,
            splitLine: {
                show: true,
                interval: 'auto',
                lineStyle: {
                    color: ['#D4DFF5']
                }
            },
            axisTick: {
                show: false
            },
            axisLine: {
                lineStyle: {
                    color: '#609ee9'
                }
            },
            axisLabel: {
                margin: 10,
                textStyle: {
                    fontSize: 14
                }
            }
        },
        yAxis: {
            type: 'value',
            splitLine: {
                lineStyle: {
                    color: ['#D4DFF5']
                }
            },
            axisTick: {
                show: false
            },
            axisLine: {
                lineStyle: {
                    color: '#609ee9'
                }
            },
            axisLabel: {
                margin: 10,
                textStyle: {
                    fontSize: 14
                }
            }
        },
        series: [{
            name: name,
            type: 'line',
            smooth: true,
            showSymbol: false,
            symbol: 'circle',
            areaStyle: {
                normal: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(199, 237, 250,0.5)'
                    }], false)
                }
            },
            itemStyle: {
                normal: {
                    color: '#3598DC'
                }
            },

            data: []


        }]
    });
    myChart.showLoading();    //数据加载完之前先显示一段简单的loading动画
    setInterval(function () {
        // login(url, user, password, key, historyType, limit, myChart);
        hostsidGet(url, auth, 'kvm-master', key, historyType, limit, myChart);
    }, time);
}

// function login(url, user, password, key, historyType, limit, myChart) {
//     $.ajax({
//         type: "post",
//         async: true,  //异步请求（同步请求将会锁住浏览器，用户其他操作必须等待请求完成才可以执行）
//         url: url,
//         contentType: "application/json",
//         data: JSON.stringify({
//             "jsonrpc": "2.0",
//             "method": "user.login",
//             "id": 1,
//             "params": {
//                 "user": user,
//                 "password": password
//             }
//         }),
//         dataType: "json",        //返回数据形式为json
//         success: function (json) {
//             //请求成功时执行该函数内容，result即为服务器返回的json对象
//             var auth = json.result;
//             console.log(auth);
//
//             hostsidGet(url, auth, 'Zabbix server', key, historyType, limit, myChart);
//
//         },
//
//         error: function (errorMsg) {
//             //请求失败时执行该函数
//             console.log(errorMsg);
//         }
//     });
// }

function hostsidGet(url, auth, hostName, key, historyType, limit, myChart) {
    $.ajax({
        type: "post",
        async: true,  //异步请求（同步请求将会锁住浏览器，用户其他操作必须等待请求完成才可以执行）
        url: url,    //请求发送到TestServlet处
        contentType: "application/json",
        data: JSON.stringify({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": [hostName]
                },
                "output": [
                    "hostid",
                    "host"
                ]
            },
            "id": 2,
            "auth": auth
        }),
        dataType: "json",        //返回数据形式为json
        success: function (json) {
            //请求成功时执行该函数内容，result即为服务器返回的json对象
            var hosts = json.result;
            // console.log(json.result[0].hostid);
            console.log(hosts);
            for (var i = 0, len = hosts.length; i < len; i++) {
                console.log(hosts[i].hostid);
                itemsGet(url, auth, hosts[i].hostid, key, historyType, limit, myChart);
            }
        },

        error: function (errorMsg) {
            //请求失败时执行该函数
            console.log(errorMsg);
        }
    });
}

function itemsGet(url, auth, hostId, key, historyType, limit, myChart) {
    $.ajax({
        type: "post",
        async: true,  //异步请求（同步请求将会锁住浏览器，用户其他操作必须等待请求完成才可以执行）
        url: url,    //请求发送到TestServlet处
        contentType: "application/json",
        data: JSON.stringify({
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": [
                    "key_",
                    "name",
                    'itemid'
                ],
                "hostids": hostId,
                "filter": {
                    "key_": key
                }
            },
            "auth": auth,
            "id": 3
        }),
        dataType: "json",        //返回数据形式为json
        success: function (json) {
            //请求成功时执行该函数内容，result即为服务器返回的json对象
            var items = json.result;
            console.log(items);

            for (var i = 0, len = items.length; i < len; i++) {
                console.log(items[i].itemid);
                historysGet(url, auth, items[i].itemid, historyType, limit, myChart);
            }
        },

        error: function (errorMsg) {
            //请求失败时执行该函数
            console.log(errorMsg);
        }
    });
}

function historysGet(url, auth, itemId, historyType, limit, myChart) {
    $.ajax({
        type: "post",
        async: true,  //异步请求（同步请求将会锁住浏览器，用户其他操作必须等待请求完成才可以执行）
        url: url,    //请求发送到TestServlet处
        contentType: "application/json",
        data: JSON.stringify({
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": historyType,
                "itemids": itemId,
                "sortfield": "clock",
                "sortorder": "DESC",
                "limit": limit
            },
            "auth": auth,
            "id": 4
        }),
        dataType: "json",        //返回数据形式为json
        success: function (json) {
            //请求成功时执行该函数内容，result即为服务器返回的json对象
            var historys = json.result;
            console.log(historys);

            var dates = [];
            var values = [];
            for (var i = 0, len = historys.length; i < len; i++) {
                dates.push(formatUnixtimestamp(historys[i].clock));
                values.push(historys[i].value);
            }
            dates.reverse();
            values.reverse();
            myChart.hideLoading();    //隐藏加载动画
            myChart.setOption({        //加载数据图表
                xAxis: {
                    data: dates
                },
                series: [{
                    // 根据名字对应到相应的系列
                    data: values
                }]
            });
        },

        error: function (errorMsg) {
            //请求失败时执行该函数
            console.log(errorMsg);
        }
    });
}

function formatUnixtimestamp(unixTimeStamp) {
    var timeStamp = new Date(unixTimeStamp * 1000);
    var year = 1900 + timeStamp.getYear();
    var month = "0" + (timeStamp.getMonth() + 1);
    var date = "0" + timeStamp.getDate();
    var hour = "0" + timeStamp.getHours();
    var minute = "0" + timeStamp.getMinutes();
    var second = "0" + timeStamp.getSeconds();
    return year + "-" + month.substring(month.length - 2, month.length) + "-" + date.substring(date.length - 2, date.length)
        + " " + hour.substring(hour.length - 2, hour.length) + ":"
        + minute.substring(minute.length - 2, minute.length) + ":"
        + second.substring(second.length - 2, second.length);
}

///////////////
