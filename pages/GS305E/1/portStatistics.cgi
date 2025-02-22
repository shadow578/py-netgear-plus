<!DOCTYPE html>
<html>
<head>
<title>Port Statistics</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css" href="/style.css?z10">
<script  src="/frame.js?z10" type="text/javascript"></script>
<script  src="/function.js?z10" type="text/javascript"></script>
</head>

<body onload="initTableCss();showCounter()">
<form method="post" action="portStatistics.cgi">
<input type="hidden" name="clearCounters" id="clearCounters" value="">
<input type=hidden name='hash' id='hash' value="140">
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
<input type="hidden" value="67">
<input type="hidden" value="824881825">
<td class="def" sel="text">824881825
</td>
<input type="hidden" value="51">
<input type="hidden" value="902781770">
<td class="def" sel="text">902781770
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">2</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="3">
<input type="hidden" value="2040182132">
<td class="def" sel="text">2040182132
</td>
<input type="hidden" value="8">
<input type="hidden" value="3313549586">
<td class="def" sel="text">3313549586
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">3</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="2">
<input type="hidden" value="72234717">
<td class="def" sel="text">72234717
</td>
<input type="hidden" value="1">
<input type="hidden" value="3537973499">
<td class="def" sel="text">3537973499
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">4</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<td class="def" sel="text">0
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<td class="def" sel="text">0
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">5</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="45">
<input type="hidden" value="2500715010">
<td class="def" sel="text">2500715010
</td>
<input type="hidden" value="56">
<input type="hidden" value="2270916050">
<td class="def" sel="text">2270916050
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
