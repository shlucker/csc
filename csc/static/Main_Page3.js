$(document).ready(function () {

    var menu = $('.topmenu');
    var origOffsetY = menu.offset().top;

    function scroll() {
        if ($(window).scrollTop() >= origOffsetY) {
            $('.topmenu').addClass('sticky');
        } else {
            $('.topmenu').removeClass('sticky');
        }


    }

    document.onscroll = scroll;

});

$(document).ready(function () {
    $("#type").change(function () {
        var val = $(this).val();
        if (val == "item1") {
            $("#size").html("<option value='test'>item1: test 1</option><option value='test2'>item1: test 2</option>");
        } else if (val == "item2") {
            $("#size").html("<option value='test'>item2: test 1</option><option value='test2'>item2: test 2</option>");
        } else if (val == "item3") {
            $("#size").html("<option value='test'>item3: test 1</option><option value='test2'>item3: test 2</option>");
        }
    });
});


$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

