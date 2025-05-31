<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<link rel="stylesheet" type="text/css" href="/login.css">
<title>NETGEAR GS308Ev4</title>
<script src="/zepto.min.js" type="text/javascript"></script>
<script src="/login.js" type="text/javascript"></script>
<script src="/b_md5.js" type="text/javascript"></script>
</head>
<body class="bodyBg">
<form name="login" action="/login.cgi" method="post" onSubmit="return false;">
  <input id="submitPwd" name="password" type="hidden" value="">
  <div class="loginBody">
    <div class="switch">
      <div class="switch-icon"><img src="/switch-logo.svg" class="switch_image"></div>
<span class="p-name">GS308Ev4</span>
    </div>
    <div class="summary">
      <span>If logging in for the first time, log in with your switch's default password which is found on the label on the bottom of the switch.</span>
    </div>
    <div class="text-field">
      <label for="password" class="pwd-label">Device Password</label>
      <div class="pwd-field"></div>
      <input class="pwd-field-text" id="password" type="password" maxlength="20" size="20" value="" autocomplete="off">
      <div>
        <hr class="hr1">
        <hr class="hr2">
      </div>
      <div onclick="toggleEye()" class="switch-eye">
        <i class="icon-eye-off show"></i>
        <i class="icon-eye-on"></i>
      </div>
    </div>
<div class='pwdErrStyle'></div>
<input type=hidden id='acptLang' value='en' disabled><input type=hidden id='rand' value='1467252539' disabled><div class="signin-button" style='cursor:pointer;'>
      <div style='height:2.75rem;' onclick="encryptPwd();submitLogin()"><a id="loginBtn" href="javaScript:void(0)" class="button-label">LOG IN</a></div>
    </div>
  </div>
  </form>
    <script type="text/javascript">
        $(document).ready(function(){
            transMultipleLang(document.body);
            $(".pwdErrStyle").html(transParamLang($(".pwdErrStyle").text()));
        });
    </script>
 </body>
</html>
