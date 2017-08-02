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

var button1 = document.getElementById("button1");
var button2 = document.getElementById("button2");
var button3 = document.getElementById("button3");

if (button1.checked){
    alert("radio1 selected");
}else if (button2.checked) {
    alert("radio2 selected");
}else if (button3.checked) {
    alert("radio3 selected");
}
