$(function () {
    $.get('/user/area', function (data) {
        var list = data.list;
        var province = $('#provice');
        $.each(list, function (i, n) {
            province.append('<option value="' + n.id + '">' + n.title + '</option>');
        });
    });

    $('#provice').change(function () {
        $.get('/user/area', {'pid': $(this).val()}, function (data) {
            var list = data.list;
            var city = $('#city').empty().append('<option value="0">请选择</option>');
            $('#district').empty().append('<option value="0">请选择</option>');
            $.each(list, function (i, n) {
                city.append('<option value="' + n.id + '">' + n.title + '</option>');
            });
        });
    });
    $('#city').change(function () {
        $.get('/user/area', {'pid': $(this).val()}, function (data) {
            var list = data.list;
            var district = $('#district').empty().append('<option value="0">请选择</option>');
            $.each(list, function (i, n) {
                district.append('<option value="' + n.id + '">' + n.title + '</option>');
            });
        });
    });
});
