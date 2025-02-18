<!DOCTYPE html>
<html>
<head>
<title>Port Statistics</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css" href="/style.css?a1.6.0.15">
<script  src="/frame.js?a1.6.0.15" type="text/javascript"></script>
<script  src="/function.js?a1.6.0.15" type="text/javascript"></script>
</head>

<body onload="initTableCss();showCounter()">
<form method="post" action="portStatistics.cgi">
<input type="hidden" name="clearCounters" id="clearCounters" value="">
<input type=hidden name='hash' id='hash' value="32163">
</form>
<form method="get" action="portStatistics.cgi">
<table class="detailsAreaContainer">
<tr>
<td><table class="tableStyle">
<tr>
<script>tbhdr('Port Statistics','portStatistics')</script>
</tr>
<tr><td class="topTitleBottomBar" colspan="2"></td></tr>
<tr><td class="paddingTableBody" colspan="2"><table class="tableStyle" id="tbl2" style='width:728px;'>
<tr>
<tr><td class="def_TH">Port</td>
<td class="def_TH spacer30Percent">Bytes Received</td>
<td class="def_TH spacer30Percent">Bytes Sent</td>
<td class="def_TH spacer30Percent">CRC Error Packets</td></tr>
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">1</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="7">
<input type="hidden" value="2941794766">
<td class="def" sel="text">2941794766
</td>
<input type="hidden" value="7">
<input type="hidden" value="2935721308">
<td class="def" sel="text">2935721308
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">2</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="3">
<input type="hidden" value="3790266192">
<td class="def" sel="text">3790266192
</td>
<input type="hidden" value="2">
<input type="hidden" value="197679212">
<td class="def" sel="text">197679212
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">3</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="0">
<input type="hidden" value="2892169043">
<td class="def" sel="text">2892169043
</td>
<input type="hidden" value="0">
<input type="hidden" value="3592320234">
<td class="def" sel="text">3592320234
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">4</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="0">
<input type="hidden" value="681249536">
<td class="def" sel="text">681249536
</td>
<input type="hidden" value="2">
<input type="hidden" value="774263004">
<td class="def" sel="text">774263004
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">5</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="3">
<input type="hidden" value="3488637005">
<td class="def" sel="text">3488637005
</td>
<input type="hidden" value="3">
<input type="hidden" value="2326198154">
<td class="def" sel="text">2326198154
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
</tr>
</table>
</td></tr>
</table>
</td></tr>
</form>
<script>
var str = CreateButtons('button','Clear Counters','submitClearCounters()','btn_Cancel','on');
str += CreateButtons('button','Refresh','submitForm()','btn_Refresh','on');
PaintButtons(str);
</script>
</body>
</html>
