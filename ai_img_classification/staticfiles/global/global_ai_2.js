function closeSplashMenu(){"use strict";$(".splash-menu").removeClass("expand"),$(".splash-menu li.selected").removeClass("selected")}function openSplashMenu(){"use strict";$(".splash-menu").addClass("expand")}$(document).ready(function(){$("ul.splash-menu-items li a").on("click",function(e){e.preventDefault();var s=$(this).attr("href");DIM.util.setCookie("LanguageSelected",s),s&&"#"!=s&&"javascript:void(0)"!=s&&(window.location.href=s)}),$(".splash-menu-items > li").on("click",function(){"use strict";var e=$(this).hasClass("selected"),s=$(this).parent(),l=$(window).width()<768;s.find(".selected").removeClass("selected"),e||$(this).addClass("selected"),$(this).closest("li").children("ul").length&&s.find(".selected").length>0?$(".splash-menu").addClass("expand"):l||$(".splash-menu").removeClass("expand")})});