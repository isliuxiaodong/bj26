$(function () {

    var error_name = false;
    var error_password = false;

    $('.name_input').blur(function () {
        check_user_name();
    });

    $('.pass_input').blur(function () {
        check_pwd()
    });


    function check_user_name() {
        var len = $('.name_input').val().length;
        if(len==0){
            $('.name_input').next().html('请输入用户名').show();
            error_name = true;
        }
        else {
            $('.name_input').next().hide();
            error_name = false;
        }
    }

    function check_pwd() {
        var len = $('.pass_input').val().length;
        if (len == 0) {
            $('.pass_input').next().html('请输入密码').show();
            error_password = true;
        }
        else {
            $('.pass_input').next().hide();
            error_password = false;
        }
    }

    $('.input_submit').submit(function () {
        check_user_name()
        check_pwd()
        if(error_name == false && error_password ==false){
            return true;
        }
        else
        {
            return false
        }
    })
});
