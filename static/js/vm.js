var list1 = document.getElementsByName('address');
for (var i = 0; i < list1.length; i++) {
    list1[i].removeAttribute('class');
    list1[i].addEventListener('click', function () {
        for (var i = 0; i < list1.length; i++) {
            list1[i].removeAttribute('class');
        }
        this.setAttribute('class', 'after')
    })
}

var list2 = document.getElementsByName('sys');
for (var i = 0; i < list2.length; i++) {
    list2[i].removeAttribute('class');
    list2[i].addEventListener('click', function () {
        for (var i = 0; i < list2.length; i++) {
            list2[i].removeAttribute('class');
        }
        this.setAttribute('class', 'after')
    })
}

var list3 = document.getElementsByName('usetime');
for (var i = 0; i < list3.length; i++) {
    list3[i].removeAttribute('class');
    list3[i].addEventListener('click', function () {
        for (var i = 0; i < list3.length; i++) {
            list3[i].removeAttribute('class');
        }
        this.setAttribute('class', 'after')
    })
}


$(function () {
    $('.serverli input').click(function () {
        if ($('.serverli input').hasClass('addrdown')) {
            $('.serverli input').removeClass('addrdown');
            $(this).addClass('addrdown');
        } else {
            $(this).addClass('addrdown');
        }
    });

    $('.addrli input').click(function () {
        if ($('.addrli input').hasClass('addrdown')) {
            $('.addrli input').removeClass('addrdown');
            $(this).addClass('addrdown');
        } else {
            $(this).addClass('addrdown');
        }
    });

    $('.addressli input').click(function () {
        if ($('.addressli input').hasClass('addrdown')) {
            $('.addressli input').removeClass('addrdown');
            $(this).addClass('addrdown');
        } else {
            $(this).addClass('addrdown');
        }
    });

    $('.sysli').click(function () {
        if ($('.sysli').hasClass('syswindown')) {
            $('.sysli').removeClass('syswindown');
            $(this).addClass('syswindown');
        } else {
            $(this).addClass('syswindown');
        }
    });

    $('.usetimeli input').click(function () {
        if ($('.usetimeli input').hasClass('usetimedown')) {
            $('.usetimeli input').removeClass('usetimedown');
            $(this).addClass('usetimedown');
        } else {
            $(this).addClass('usetimedown');
        }
    });

    $('.installwayli input').click(function () {
        if ($('.installwayli input').hasClass('installwaydown')) {
            $('.installwayli input').removeClass('installwaydown');
            $(this).addClass('installwaydown');
        } else {
            $(this).addClass('installwaydown');
        }
    });

});