//保存折线图实时数据
let LineData = {};   //三条折线
LineData["CPU"] = [];
LineData["mem"] = [];
LineData["disk"] = [];
let xAxis_data = [];
let currentNode_name = "Zabbix server_1";

//页面初次加载初始化
function initFirst() {
    var zNodes = [];
    $.ajax({
        type: "POST",
        url: "/res/getSources/",
        success: function (data) {
            console.log("1111")
            console.log(date)
            initTree(data);
             //顶部信息
            renderTopRigth(data.all_node_info);
            window.setTimeout("initFirst()", 10000)
        },
        error: function () {
        }
    })
}


//左侧数量与ztree数据初始化
function initTree(data) {
    console.log(data.host);
    var settingss = {
        data: {
            simpleData: {
                enable: true, //true 、 false 分别表示 使用 、 不使用 简单数据模式
                idKey: "id", //节点数据中保存唯一标识的属性名称
                pIdKey: "parentId", //节点数据中保存其父节点唯一标识的属性名称
                rootPId: -1 //用于修正根节点父节点数据，即 pIdKey 指定的属性值
            },
            key: {
                name: "menuName", //zTree 节点数据保存节点名称的属性名称  默认值："name"
            }

        },
        callback: {
            onClick: showModal,
        }
    };
    //zTree点击事件
    var leidaDom = document.getElementById('leida_table');
    var jisuanDom = document.getElementById('jisuan_table');
    var wuqiDom = document.getElementById('wuqi_table');
    var errDom = document.getElementById('err_info');

    function showModal(event, treeId, treeNode) {
        if (treeNode.iconSkin == 'hostgroup') {
            LineData["CPU"] = [];
            LineData["mem"] = [];
            LineData["disk"] = [];
            xAxis_data = [];      //清空折线信息
            // alert(treeNode.name)
            currentNode_name = treeNode.menuName;
            getServerInfo()
        } else {
            let url = "/res/get_res_info/";
            let data = {'res':treeNode.menuName};
            if (treeNode.iconSkin === 'leida') {

                // onlyshow(leidaDom, errDom, jisuanDom, wuqiDom); //这句话显示列表，点击雷达用来测试样式
                $.ajax({
                    type:'POST',
                    url: url,
                    data:data,
                    dataType: 'json',
                    success(data)
                {
                    showLeida(data.dataInfo);
                }
            ,
                error()
                {
                    onlyshow(errDom, leidaDom, jisuanDom, wuqiDom);
                }
            }
            )
            } else if (treeNode.iconSkin === 'jisuan') {
                //onlyshow(jisuanDom, errDom, leidaDom, wuqiDom)
                $.ajax({
                    type:'POST',
                    url: url,
                    dataType: 'json',
                    data:data,
                    success(data) {
                        showJisuan(data.dataInfo)
                    },
                    error() {
                        onlyshow(errDom, leidaDom, jisuanDom, wuqiDom);
                    }
                })
            } else if (treeNode.iconSkin === 'wuqi') {
                // onlyshow(wuqiDom, errDom, leidaDom, jisuanDom)
                $.ajax({
                    type:'POST',
                    url: url,
                    data:data,
                    dataType: 'json',
                    success(data) {
                        showWuqi(data.dataInfo)
                    },
                    error() {
                        onlyshow(errDom, leidaDom, jisuanDom, wuqiDom);
                    }
                })
            }
            $('#myModal').modal('show');
        }
    }

    function showLeida(data) {
        document.getElementById('rsid').innerText = data.rsid;
        document.getElementById('rsname').innerText = data.rsname;
        document.getElementById('rtype').innerText = data.rtype;
        document.getElementById('rop_band').innerText = data.rop_band+"/mhz";
        document.getElementById('rpulse_width').innerText = data.rpulse_width+"/mhz";
        document.getElementById('rantenna_gain').innerText = data.rantenna_gain+"/db";
        document.getElementById('rpulse_freg').innerText = data.rpulse_freq+"/khz";
        document.getElementById('rtrans_power').innerText = data.rtrans_power+"/kw";
        document.getElementById('rradius_max').innerText = data.rradius_max+"/m";
        document.getElementById('rdist_max').innerText = data.rdist_max+"/m";

        onlyshow(leidaDom, jisuanDom, wuqiDom, errDom);

    }

    function showJisuan(data) {
        document.getElementById('csid').innerText = data.csid;
        document.getElementById('csname').innerText = data.csname;
        document.getElementById('ctype').innerText = data.ctype;
        document.getElementById('caccuracy').innerText = data.caccuracy;

        onlyshow(jisuanDom, leidaDom, wuqiDom, errDom);
    }

    function showWuqi(data) {
        document.getElementById('asid').innerText = data.asid;
        document.getElementById('asname').innerText = data.asname;
        document.getElementById('atype').innerText = data.atype;
        document.getElementById('aspeed').innerText = data.aspeed+"/ma";
        document.getElementById('akill_radius').innerText = data.akill_radius+"/m";
        document.getElementById('ahit_rate').innerText = data.ahit_rate+"/%";
        document.getElementById('aguide_accuracy').innerText = data.aguide_accuracy+"/m";
        document.getElementById('ahit_accuracy').innerText = data.ahit_accuracy+"/m";
        document.getElementById('aattack_distmax').innerText = data.aattack_distmax+"/km";

        onlyshow(wuqiDom, leidaDom, jisuanDom, errDom);
    }

    //只显示第一个dom元素，其他隐藏
    function onlyshow(showdom1, dom2, dom3, dom4) {//todo多个参数
        showdom1.style.display = 'block';
        dom2.style.display = 'none';
        dom3.style.display = 'none';
        dom4.style.display = 'none';
    }

    zTreeObj = $.fn.zTree.init($("#treeDemo"), settingss, data.host); //初始化树
    zTreeObj.expandAll(true); //true 节点全部展开、false节点收缩
    $("#radar_count").text(data.radar_count + "个");
    $("#compute_resource_count").text(data.computer_resource_count + "个");
    $("#weapon_count").text(data.weapon_count + "个");
}

//接入机型占比 1. 资源池
function renderChartBar01(radar_count, computer_resource_count, weapon_count) {
    var myChart = echarts.init(document.getElementById("layer1"));
    var seriesData = [{
        name: "武器",
        value: weapon_count
    }, {
        name: "计算资源",
        value: computer_resource_count
    }, {
        name: "雷达",
        value: radar_count
    }];
    var legendData = ["武器", "计算资源", "雷达"]
    var colorList = ['#73ACFF', '#FDB36A', '#9E87FF'];
    option = {
        title: {
            text: '资源池',
            top: '47%',
            left: '37%',
            textStyle: {
                color: '#fff'
            }
        },
        tooltip: {
            trigger: 'item',
            borderColor: 'rgba(255,255,255,.3)',
            backgroundColor: 'rgba(13,5,30,.6)',
            borderWidth: 1,
            padding: 5,
            formatter: function (parms) {
                var str = parms.marker + "" + parms.data.name + "</br>" +
                    "数量：" + parms.data.value + "台</br>" +
                    "占比：" + parms.percent + "%";
                return str;
            }
        },
        legend: {
            type: "scroll",
            orient: 'vertical',
            right: 0,
            align: 'auto',
            top: 0,
            textStyle: {
                color: '#fff'
            },
            data: legendData
        },
        series: [{
            type: 'pie',
            z: 3,
            center: ['45%', '55%'],
            radius: ['55%', '70%'],
            clockwise: true,
            avoidLabelOverlap: true,
            hoverOffset: 15,
            itemStyle: {
                normal: {
                    color: function (params) {
                        return colorList[params.dataIndex]
                    }
                }
            },
            label: {
                show: true,
                position: 'outside',
                formatter: '{a|{b}：{d}%}\n{hr|}',
                rich: {
                    hr: {
                        backgroundColor: 't',
                        borderRadius: 3,
                        width: 3,
                        height: 3,
                        padding: [3, 3, 0, -12]
                    },
                    a: {
                        padding: [-30, 15, -20, 15]
                    }
                }
            },
            labelLine: {
                normal: {
                    length: 20,
                    length2: 30,
                    lineStyle: {
                        width: 1
                    }
                }
            },
            data: seriesData
        }, {
            name: '第一层环',
            type: 'pie',
            z: 2,
            tooltip: {
                show: false
            },
            center: ['45%', '55%'],
            radius: ['60%', '70%'],
            hoverAnimation: false,
            clockWise: false,
            itemStyle: {
                normal: {
                    color: 'rgba(1,15,80,.4)',
                },
                emphasis: {
                    color: 'rgba(1,15,80,.4)',
                }
            },
            label: {
                show: false
            },
            data: [100]
        }, {
            name: '第二层环',
            type: 'pie',
            z: 1,
            tooltip: {
                show: false
            },
            center: ['45%', '55%'],
            radius: ['70%', '90%'],
            hoverAnimation: false,
            clockWise: false,
            itemStyle: {
                normal: {
                    shadowBlur: 40,
                    shadowColor: 'rgba(0, 255, 255,.5)',
                    color: 'rgba(0,15,69,.5)',
                },
                emphasis: {
                    color: 'rgba(0,15,69,.2)',
                }
            },
            label: {
                show: false
            },
            data: [100]
        }]
    };
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}


//3. 复合曲线图 平台实时监测信息  //硬盘
function renderLayer04Left() {
    var myChart = echarts.init(document.getElementById("layer2"));
    option = {
        color: ['#ffd285', '#ff733f', '#ec4863'],
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            top: 0,
            right: 0,
            textStyle: {
                color: '#ffd285',
            },
            data: ['硬盘']
        },
        grid: {
            left: '1%',
            right: 0,
            top: '10%',
            bottom: '6%',
            containLabel: true
        },
        toolbox: {
            "show": false,
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            "axisLine": {
                lineStyle: {
                    color: '#c0576d'
                }
            },
            "axisTick": {
                "show": false
            },
            axisLabel: {
                textStyle: {
                    color: '#ffd285'
                }
            },
            boundaryGap: false,
            data: xAxis_data
        },
        yAxis: {
            "axisLine": {
                lineStyle: {
                    color: '#c0576d'
                }
            },
            splitLine: {
                show: false,
                lineStyle: {
                    color: '#c0576d'
                }
            },
            "axisTick": {
                "show": false
            },
            axisLabel: {
                textStyle: {
                    color: '#ffd285'
                }
            },
            type: 'value'
        },
        series: [{
            name: '硬盘',
            smooth: true,
            type: 'line',
            symbolSize: 8,
            symbol: 'circle',
            data: LineData["disk"]
        }]
    }
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}


//4. 右下方三个饼图
function renderLayer04Right(dataArr) {
    var myChart = echarts.init(document.getElementById("layer3"));
    var placeHolderStyle = {
        normal: {
            label: {
                show: false
            },
            labelLine: {
                show: false
            },
            color: "rgba(0,0,0,0)",
            borderWidth: 0
        },
        emphasis: {
            color: "rgba(0,0,0,0)",
            borderWidth: 0
        }
    };
    var dataStyle = {
        normal: {
            formatter: '使用率{c}%',
            position: 'center',
            show: true,
            textStyle: {
                fontSize: '14',
                fontWeight: 'normal',
                color: '#AAAFC8'
            }
        }
    };
    option = {
        title: [{
            text: 'CPU',
            left: '20%',
            top: '60%',
            textAlign: 'center',
            textStyle: {
                fontWeight: 'normal',
                fontSize: '20',
                color: '#fff',
                textAlign: 'center',
            },
        }, {
            text: '内存',
            left: '50%',
            top: '60%',
            textAlign: 'center',
            textStyle: {
                color: '#fff',
                fontWeight: 'normal',
                fontSize: '20',
                textAlign: 'center',
            },
        }, {
            text: '硬盘',
            left: '80%',
            top: '60%',
            textAlign: 'center',
            textStyle: {
                color: '#fff',
                fontWeight: 'normal',
                fontSize: '20',
                textAlign: 'center',
            },
        }],

        //第一个图表
        series: [{
            type: 'pie',
            hoverAnimation: false, //鼠标经过的特效
            radius: ['65%', '70%'],
            center: ['20%', '50%'],
            startAngle: 225,
            labelLine: {
                normal: {
                    show: false
                }
            },
            label: {
                normal: {
                    position: 'center'
                }
            },
            data: [{
                value: 100,
                itemStyle: {
                    normal: {
                        color: ['rgba(176, 212, 251, 0.3)']
                    }
                },
            }, {
                value: 35,
                itemStyle: placeHolderStyle,
            },

            ]
        },
            //上层环形配置
            {
                type: 'pie',
                hoverAnimation: false, //鼠标经过的特效
                radius: ['65%', '70%'],
                center: ['20%', '50%'],
                startAngle: 225,
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                label: {
                    normal: {
                        position: 'center'
                    }
                },
                data: [{
                    value: dataArr.cpu,
                    "itemStyle": {
                        "normal": {
                            "color": new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                "offset": 0,
                                "color": '#00cefc'
                            }, {
                                "offset": 1,
                                "color": '#367bec'
                            }]),
                        }
                    },
                    label: dataStyle,
                }, {
                    value: 100 - dataArr.cpu,
                    itemStyle: placeHolderStyle,
                },

                ]
            },


            //第二个图表
            {
                type: 'pie',
                hoverAnimation: false,
                radius: ['65%', '70%'],
                center: ['50%', '50%'],
                startAngle: 225,
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                label: {
                    normal: {
                        position: 'center'
                    }
                },
                data: [{
                    value: 100,
                    itemStyle: {
                        normal: {
                            color: ['rgba(176, 212, 251, 0.3)']
                        }
                    },

                }, {
                    value: 35,
                    itemStyle: placeHolderStyle,
                },

                ]
            },

            //上层环形配置
            {
                type: 'pie',
                hoverAnimation: false,
                radius: ['65%', '70%'],
                center: ['50%', '50%'],
                startAngle: 225,
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                label: {
                    normal: {
                        position: 'center'
                    }
                },
                data: [{
                    value: dataArr.mem,
                    "itemStyle": {
                        "normal": {
                            "color": new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                "offset": 0,
                                "color": '#9FE6B8'
                            }, {
                                "offset": 1,
                                "color": '#32C5E9'
                            }]),
                        }
                    },
                    label: dataStyle,
                }, {
                    value: 100 - dataArr.mem,
                    itemStyle: placeHolderStyle,
                },

                ]
            },
            //第三个图表
            {
                type: 'pie',
                hoverAnimation: false,
                radius: ['65%', '70%'],
                center: ['80%', '50%'],
                startAngle: 225,
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                label: {
                    normal: {
                        position: 'center'
                    }
                },
                data: [{
                    value: 100,
                    itemStyle: {
                        normal: {
                            color: ['rgba(176, 212, 251, 0.3)']
                        }
                    },

                }, {
                    value: 35,
                    itemStyle: placeHolderStyle,
                },

                ]
            },

            //上层环形配置
            {
                type: 'pie',
                hoverAnimation: false,
                radius: ['65%', '70%'],
                center: ['80%', '50%'],
                startAngle: 225,
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                label: {
                    normal: {
                        position: 'center'
                    }
                },
                data: [{
                    value: dataArr.disk,
                    "itemStyle": {
                        "normal": {
                            "color": new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                "offset": 0,
                                "color": '#FDFF5C'
                            }, {
                                "offset": 1,
                                "color": '#FFDB5C'
                            }]),
                        }
                    },
                    label: dataStyle,
                }, {
                    value: 100 - dataArr.disk,
                    itemStyle: placeHolderStyle,
                },

                ]
            },
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

//5. 复合曲线拆分：CPU
function renderCPU() {
    var myChart = echarts.init(document.getElementById("CPU"));
    option = {
        color: ['#ff733f'],
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            top: 0,
            right: 0,
            textStyle: {
                color: '#ffd285',
            },
            data: ['CPU']
        },
        grid: {
            left: '1%',
            right: 0,
            top: '10%',
            bottom: '6%',
            containLabel: true
        },
        toolbox: {
            "show": false,
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            "axisLine": {
                lineStyle: {
                    color: '#c0576d'
                }
            },
            "axisTick": {
                "show": false
            },
            axisLabel: {
                textStyle: {
                    color: '#ffd285'
                }
            },
            boundaryGap: false,
            data: xAxis_data
        },
        yAxis: {
            "axisLine": {
                lineStyle: {
                    color: '#c0576d'
                }
            },
            splitLine: {
                show: false,
                lineStyle: {
                    color: '#c0576d'
                }
            },
            "axisTick": {
                "show": false
            },
            axisLabel: {
                textStyle: {
                    color: '#ffd285'
                }
            },
            type: 'value'
        },
        series: [{
            name: 'CPU',
            smooth: true,
            type: 'line',
            symbolSize: 8,
            symbol: 'circle',
            data: LineData["CPU"]
        }]
    }
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

//6.复合曲线拆分：内存
function renderMem() {
    var myChart = echarts.init(document.getElementById("mem"));
    option = {
        color: ['#ec4863'],
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            top: 0,
            right: 0,
            textStyle: {
                color: '#ffd285',
            },
            data: ['内存']
        },
        grid: {
            left: '1%',
            right: 0,
            top: '10%',
            bottom: '6%',
            containLabel: true
        },
        toolbox: {
            "show": false,
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            "axisLine": {
                lineStyle: {
                    color: '#c0576d'
                }
            },
            "axisTick": {
                "show": false
            },
            axisLabel: {
                textStyle: {
                    color: '#ffd285'
                }
            },
            boundaryGap: false,
            data: xAxis_data
        },
        yAxis: {
            "axisLine": {
                lineStyle: {
                    color: '#c0576d'
                }
            },
            splitLine: {
                show: false,
                lineStyle: {
                    color: '#c0576d'
                }
            },
            "axisTick": {
                "show": false
            },
            axisLabel: {
                textStyle: {
                    color: '#ffd285'
                }
            },
            type: 'value'
        },
        series: [{
            name: '内存',
            smooth: true,
            type: 'line',
            symbolSize: 8,
            symbol: 'circle',
            data: LineData["mem"]
        },]
    }
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

//右上方10个平台数据
function renderTopRigth(all_node_info) {
    //动态生成顶部平台数据展示
    var a = '';
    for (var i = 0; i < all_node_info.length; i++) {
        a += '<div id="server_' + (i + 1) + '"  class="server_out"></div>';
    }
    document.getElementById('top_right-border').innerHTML = a;
    for (let i = 0; i <all_node_info.length; i++) {
        var myChart = echarts.init(document.getElementById("server_" + (i+1)));
        data = [
            {
                name: "CPU占用率",
                value: all_node_info[i].node_info.cpu
            },
            {
                name: "内存占用率",
                value: all_node_info[i].node_info.mem
            },
            {
                name: "硬盘占用率",
                value: all_node_info[i].node_info.disk
            }
        ];
        arrName = getArrayValue(data, "name");
        arrValue = getArrayValue(data, "value");

        objData = array2obj(data, "name");
        optionData = getData(data)

        function getArrayValue(array, key) {
            var key = key || "value";
            var res = [];
            if (array) {
                array.forEach(function (t) {
                    res.push(t[key]);
                });
            }
            return res;
        }

        function array2obj(array, key) {
            var resObj = {};
            for (var i = 0; i < array.length; i++) {
                resObj[array[i][key]] = array[i];
            }
            return resObj;
        }

        function getData(data) {
            var res = {
                series: [],
                yAxis: []
            };
            for (let i = 0; i < data.length; i++) {
                // console.log([70 - i * 15 + '%', 67 - i * 15 + '%']);
                res.series.push({
                    name: '',
                    type: 'pie',
                    clockWise: false, //顺时加载
                    hoverAnimation: false, //鼠标移入变大
                    radius: [73 - i * 10 + '%', 68 - i * 10 + '%'],
                    center: ["35%", "50%"],
                    label: {
                        normal: {
                            show: false,
                            position: 'inside'
                        }
                    },
                    itemStyle: {
                        normal: {
                            label: {
                                show: false,
                            },
                            labelLine: {
                                show: false
                            },
                            borderWidth: 5,
                        }

                    },
                    data: [
                        {
                            value: data[i].value,
                            name: data[i].name
                        }, {
                            value: 100 - data[i].value,
                            name: '',
                            itemStyle: {
                                normal: {
                                    color: "rgba(3, 31, 62,0)",
                                    borderWidth: 0
                                }
                            },
                            tooltip: {
                                show: false
                            },
                            hoverAnimation: false
                        }]
                });
                res.series.push({
                    name: '',
                    type: 'pie',
                    silent: true,
                    z: 1,
                    clockWise: false, //顺时加载
                    hoverAnimation: false, //鼠标移入变大
                    radius: [73 - i * 10 + '%', 68 - i * 10 + '%'],
                    center: ["35%", "50%"],
                    label: {
                        normal: {
                            show: false,
                            position: 'inside'
                        }
                    },
                    itemStyle: {
                        normal: {
                            label: {
                                show: false,
                            },
                            labelLine: {
                                show: false
                            },
                            borderWidth: 5,
                        }
                    },
                    data: [{
                        value: 7.5,
                        itemStyle: {
                            normal: {
                                color: "rgb(3, 31, 62)",
                                borderWidth: 0
                            }

                        },
                        tooltip: {
                            show: false
                        },
                        hoverAnimation: false
                    }, {
                        value: 2.5,
                        name: '',
                        itemStyle: {
                            normal: {
                                color: "rgba(3, 31, 62,0)",
                                borderWidth: 0
                            }
                        },
                        tooltip: {
                            show: false
                        },
                        hoverAnimation: false
                    }]
                });
                res.yAxis.push(data[i].value + "%");
            }
            return res;
        }

        option = {
            title: [{
                text: all_node_info[i].node_name,
                bottom: '0px',
                left: '30%',
                textStyle: {
                    color: '#fff',
                    fontSize: '11px',
                },

            },{
                text: '{a|导弹数}\n{b|' + all_node_info[i].node_info.node_weapon_count + '个}',
                top: '37%',
                left: '25%',
                textStyle: {
                    color: '#fff',
                        textAlign:'center',
                    rich:{
                         a:{
                            fontSize:18,
                            color:'#ffffff',
                        },
                        b:{
                            fontSize:23,
                            color:'#ffac50',
                            padding:[10,0],
                        }
                    }
                }
            }],
            legend: {
                show: true,
                icon: "circle",
                top: "8%",
                right: 0,
                data: arrName,
                width: 40,
                padding: [0, 5],
                itemGap: 10,
                formatter: function (name) {
                    return "{title|" + name + "}{value|  " + (objData[name].value) + "%}"
                },

                textStyle: {
                    rich: {
                        title: {
                            fontSize: 10,
                            lineHeight: 4,
                            color: "rgb(0, 178, 246)"
                        },
                        value: {
                            fontSize: 12,
                            lineHeight: 2,
                            color: "#fff"
                        }
                    }
                },
            },
            tooltip: {
                show: true,
                trigger: "item",
                formatter: "{a}<br>{b}:{c}({d}%)"
            },
            color: ['rgb(24, 183, 142)', 'rgb(1, 179, 238)', 'rgb(22, 75, 205)', 'rgb(52, 52, 176)'],
            xAxis: [{
                show: false
            }],
            series: optionData.series
        };
        myChart.setOption(option);
        window.addEventListener("resize", function () {
            myChart.resize();
        });
    }
}

//实时请求CPU、内存、硬盘信息
function getServerInfo() {
    $.ajax({
        type: "POST",
        url: "/res/get_node_info/",
        data: {'node_name': currentNode_name},
        success: function (data) {
            dataArr = data.data;
            renderLayer04Right(dataArr);
            initLineData(dataArr);
            renderChartBar01(data.radar_count, data.computer_resource_count, data.weapon_count)
            window.setTimeout("getServerInfo(currentNode_name)", 10000)
        }
    });
}

//封装折线图信息
function initLineData(dataArr) {
    xAxis_data.push(dataArr.time);
    LineData["CPU"].push(dataArr.cpu);
    LineData["mem"].push(dataArr.mem);
    LineData["disk"].push(dataArr.disk);
    renderCPU();
    renderMem();
    renderLayer04Left();

}

function get10MinutesScale() {
    var currDate = new Date();
    var odd = currDate.getMinutes() % 10;
    var returnArr = new Array();
    currDate.setMinutes(currDate.getMinutes() - odd);
    for (var i = 0; i < 7; i++) {
        returnArr.push(currDate.getHours() + ":" + (currDate.getMinutes() < 10 ? ("0" + currDate.getMinutes()) : currDate.getMinutes()));
        currDate.setMinutes(currDate.getMinutes() - 10);
    }
    return returnArr;
}


function getLatestDays(num) {
    var currentDay = new Date();
    var returnDays = [];
    for (var i = 0; i < num; i++) {
        currentDay.setDate(currentDay.getDate() - 1);
        returnDays.push((currentDay.getMonth() + 1) + "/" + currentDay.getDate());
    }
    return returnDays;
}
