/**
 * Created by Ciel on 2016/10/21.
 */var ver = null;
    $(function () {

        var times =60;
        var timer=null;
        $("#send").on("click", function(){
            phone = $("#phone").val();
            if (phone == "") {
                alert("请填写手机号！");
                return
            }
            ver = verification(6);
            var that = this;
            this.disabled = true;
            timer = setInterval(function(){
                times --;
                that.value = times + "秒后重试";
                if(times <= 0){
                    that.disabled = false;
                    that.value = "发送验证码";
                    clearInterval(timer);
                    times = 60;
                    ver = null;
                }
            },1000);

            data = {
                sn: 'DXX-MDQ-100-00055',
                pwd: 'F1691D19871771AC72E58CE538A6334E',
                mobile: phone,
                content: '您的验证码为 ' + ver + ' ，感谢您对Insta360的支持和关注,祝您生活愉快!【岚锋创视】'
            };
            $.post("http://sdk2.entinfo.cn:8061/mdsmssend.ashx", data, function(data,status){

            });
        });
        var chars = ['0','1','2','3','4','5','6','7','8','9'];
        function verification(n) {
             var res = "";
             for(var i = 0; i < n ; i ++) {
                 var id = Math.floor(Math.random()*10);
                 res += chars[id];
             }
             return res;
        }
    });