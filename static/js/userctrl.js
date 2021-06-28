$(function () {

    /*左侧导航栏显示隐藏功能*/
    $(".subNav").click(function () {
        /*显示*/
        if ($(this).find("span:first-child").attr('class') == "title-icon glyphicon glyphicon-chevron-down") {
            $(this).find("span:first-child").removeClass("glyphicon-chevron-down");
            $(this).find("span:first-child").addClass("glyphicon-chevron-up");
            $(this).removeClass("sublist-down");
            $(this).addClass("sublist-up");
        }
        /*隐藏*/
        else {
            $(this).find("span:first-child").removeClass("glyphicon-chevron-up");
            $(this).find("span:first-child").addClass("glyphicon-chevron-down");
            $(this).removeClass("sublist-up");
            $(this).addClass("sublist-down");
        }
        // 修改数字控制速度， slideUp(500)控制卷起速度
        $(this).next(".navContent").slideToggle(300).siblings(".navContent").slideUp(300);
    })
    /*左侧导航栏缩进功能*/
    $(".left-main .sidebar-fold").click(function () {

        if ($(this).parent().attr('class') == "left-main left-full") {
            $(".sidebar-fold").parent().hide();
            $("#div_close").show();
            $("#control_div_close").show()
            $(".dashboard-wrapper").css("margin-left", 50);
            $(this).parent().removeClass("left-full");
            $(this).parent().addClass("left-off");

            $(this).parent().parent().find(".right-product").removeClass("right-full");
            $(this).parent().parent().find(".right-product").addClass("right-off");

        }
        else {
            $(this).parent().show()
            $("#btn_close").hide();
            $(this).parent().removeClass("left-off");
            $(this).parent().addClass("left-full");

            $(this).parent().parent().find(".right-product").removeClass("right-off");
            $(this).parent().parent().find(".right-product").addClass("right-full");

        }
    })

    $('#btn_close').click(function () {
        $(".left-main").show();
        $("#div_close").hide();
        $("#control_div_close").hide()
        $(".dashboard-wrapper").css("margin-left", 170);
        $(".left-main").removeClass("left-off");
        $(".left-main").addClass("left-full");

        $(".left-main").parent().find(".right-product").removeClass("right-off");
        $(".left-main").parent().find(".right-product").addClass("right-full");
    })

    $('#control_btn_close').click(function () {
        $(".left-main").show();
        $("#div_close").hide();
        $("#control_div_close").hide()
        $(".dashboard-wrapper").css("margin-left", 170);
        $(".left-main").removeClass("left-off");
        $(".left-main").addClass("left-full");

        $(".left-main").parent().find(".right-product").removeClass("right-off");
        $(".left-main").parent().find(".right-product").addClass("right-full");
    })

    /*左侧鼠标移入提示功能*/
    $(".sBox ul li").mouseenter(function () {
        if ($(this).find("span:last-child").css("display") == "none") {
            $(this).find("div").show();
        }
    }).mouseleave(function () {
        $(this).find("div").hide();
    })
    $('#modifyVM').click(function () {
        $("#myModal").modal('show');
        console.log("打开静态框oo")
    })

    $('#applyPort').click(function () {
        $('#myModal2').modal('show');
    })

    $("#importVM").click(function(){
        $("#vmip").val("");
        $("#port").val("");
        $("#username").val("");
        $("#password").val("");
        $("#importModal").modal("show");
    })

    $("#change_info").click(function(){
        $("#ChangeInfoModal").modal("show");
    })

    $("#change_pwd").click(function(){
        $("#ChangePwdModal").modal("show");
    })

    $(".optimistic").click(function () {
        $('#op_setting').modal('show');
    })
    $('#submit1').click(function () {
        $('#form-settings').submit();

    })

    $('#submit2').click(function () {
        $('#form-port').submit();

    })

    $('#show_progress').click(function () {
        $.ajax({
            url: "/admins/get_progress/",
            type: "GET",
            data: progress,
            success: function (data) {
                data = JSON.parse(data);
                while (true) {
                    if (data[progress] == 100) {
                        alert("success!")
                        break;
                    }
                    else {
                        alert("012345");
                    }
                }
            }
        })

    })

    $('#inuse').click(function () {
        $(":checkbox:checked").each(function () {
            vm_name = $('input[type=checkbox]:checked').closest('tr').find('td:eq(2)').map(function () {
                return this.innerHTML
            }).get().join();
            $.ajax({
                type: "POST",
                data: {'vm_name': vm_name},
                url: "/users/vnc/",
                success: function (data) {
                    if (data["st"] === 1) {
                        avnc = data["index"];
                        window.open(avnc, '_blank').location;
                    } else {
                        alert("失败");
                    }
                },
                error: function () {
                    alert("false");
                }
            })
        });
    })

    $('#shutdownVM').click(function () {
        $(":checkbox:checked").each(function () {
            vm_name = $('input[type=checkbox]:checked').closest('tr').find('td:eq(2)').map(function () {
                return this.innerHTML
            }).get().join();
            $.ajax({
                type: "POST",
                data: {'vm_name': vm_name},
                url: "/vm/shutdown_vm/",
                success: function (data) {
                    if (data["st"] === 1) {
                        alert("成功");
                        window.location.reload();
                    } else {
                        alert("失败");
                    }
                },
                error: function () {
                    alert("false");
                }
            })
        });
    })


    $('#startVM').click(function () {
        $(":checkbox:checked").each(function () {
            vm_name = $('input[type=checkbox]:checked').closest('tr').find('td:eq(2)').map(function () {
                return this.innerHTML
            }).get().join();
            $.ajax({
                type: "POST",
                data: {'vm_name': vm_name},
                url: "/vm/start_vm/",
                success: function (data) {
                    if (data["st"] === 1) {
                        alert("成功");
                        window.location.reload();
                    } else {
                        alert("失败");
                    }
                },
                error: function () {
                    alert("false");
                }
            })
        });
    })


    $("#upgrade_set").click(function () {
        $(":checkbox:checked").each(function () {

            vmid = $('input[type=checkbox]:checked').closest('tr').find('td:eq(1)').map(function () {
                return this.innerHTML
            }).get().join();
            vmcpu = $('input[type=checkbox]:checked').closest('tr').find('td:eq(3)').map(function () {
                return this.innerHTML
            }).get().join();
            vmmemory = $('input[type=checkbox]:checked').closest('tr').find('td:eq(4)').map(function () {
                return this.innerHTML
            }).get().join();
            console.log(vmcpu);
            console.log(vmmemory);

            $.ajax({
                type: "POST",
                data: {
                    'vmname2': vmid,
                    'vmcpu': vmcpu,
                    'vmMemory': vmmemory
                },
                url: "/admins/q_learning/",
                success: function (data) {
                    console.log(data)

                    if (data["st"] == 1) {
                        alert("申请成功")

                    }
                    else {
                        alert("申请失败")

                    }
                },
                error: function () {
                    alert("false");
                }
            })
        });

    })


    $('.domain').click(function () {
        $('#input_domain').prop('checked', 'checked');
        document.getElementById('dmform').action = '/users/vnc/';
        document.getElementById('dmform').submit();
    })
    $('.addregion').click(function () {
        $('#myModal3').modal('show');
    })
    window.onload = function () {

        var n = document.getElementsByClassName("test");
        //var ra=document.getElementById("colorid").getAttribute('value');
        var style = ["red", "blue", "green", "purple"];
        var z = 0;
        for (var i = 0; i < n.length; i++) {

            if (z == style.length) {
                z = 0;
            }

            n[i].classList.add(style[z]);
            z++;
        }

    }

    $("#importSubmit").click(function () {
        var data = {};
        data["vmip"] = $("#vmip").val();
        data["port"] = $("#port").val();
        data["username"] = $("#username").val();
        data["password"] = $("#password").val();
        $.ajax({
            url:"/users/importvm/",
            data:JSON.stringify(data),
            type:"POST",
            dataType:"json",
            contentType:"application/json;charset=utf-8",
            success:function (data) {
                $("#importModal").modal("hide");
                if(data["state"] == 0){
                    $("#tipbody").text("请确保导入目标已开启，并且填入信息无误");
                }else if(data["state"] == 1){
                    $("#tipbody").text("导入成功");
                    $("#tipButton").bind("click", function(){
                        window.location.reload();
                    })
                }else{
                    $("#tipbody").text("导入对象已被认领");
                }
                $("#tipModal").modal("show");
            },
            error: function () {
                $("#importModal").modal("hide");
                $("#tipbody").text("失败");
                $("#tipModal").modal("show");
            }
        })
    })

    $("#agreeChangeInfo").click(function(){
        var username = $("#change_username").val()
        var email = $("#change_email").val()
        $.ajax({
            type: "POST",
            data: {'username': username, 'email': email},
            url: "/users/updateUserInfo/",
            success: function (data) {
                if (data["st"] === 1) {
                    alert("成功");
                    window.location.reload();
                } else if (data["st"] === 2){
                    alert("无需修改")
                } else {
                    alert("失败");
                }
            },
            error: function () {
                alert("false");
            }
        })
    })

    $("#agreeChangePwd").click(function(){
        var username = $("#username").val()
        var old_pwd = $("#old_pwd").val();
        var new_pwd = $("#new_pwd").val();
        var confirm_pwd = $("#confirm_pwd").val();
        if (old_pwd == ""){
            alert("请输入原密码")
        }else if (new_pwd == ""){
            alert("请输入新密码")
        }else if (new_pwd != confirm_pwd){
            alert("确认密码不正确")
        }else{
            $.ajax({
                type: "POST",
                data: {'old_pwd': old_pwd, 'new_pwd': new_pwd, 'username': username},
                url: "/users/user_changePwd/",
                success: function (data) {
                    if (data['st'] == 1){
                        $("#ChangePwdModal").modal('hide');
                        alert("修改成功，请重新登录");
                        window.location.href = '/users/login/';
                    }else{
                        alert("原密码错误");
                    }
                },
                error: function () {
                    alert("false");
                }
            })
        }
    })

})

