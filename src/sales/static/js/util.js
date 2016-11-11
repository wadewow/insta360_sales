/**
 * Created by Ciel on 2016/11/6.
 */

function getQueryString(name) {
     var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
     var r = window.location.search.substr(1).match(reg);
     if(r!=null && r[2] != undefined)
         return r[2];
     return ''
}