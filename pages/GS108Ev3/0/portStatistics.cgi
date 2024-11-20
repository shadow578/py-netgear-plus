<!DOCTYPE html>
<html>
<head>
<title>Port Statistics</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css" href="/style.css?v3.e">
<script  src="frame.js?v3.e" type="text/javascript"></script>
<script  src="function.js?v3.e" type="text/javascript"></script>
</head>
<body onload="initTableCss();counter()">
<form method="post" action="portStatistics.cgi">
<input type="hidden" name="clearCounters" id="clearCounters" value="">
<input type="hidden" name='hash' id='hash' value='67c16d682f8b7a5e5449fd3993ced364'>
</form>
<form method="get" action="portStatistics.cgi">
<table class="detailsAreaContainer">
<tr>
<td>
<table class="tableStyle">
<tr>
<script>tbhdrTable('Portstatistik','portStatistics')</script>
</tr>
<tr><td class="topTitleBottomBar" colspan="2"></td></tr>
<tr><td class="paddingTableBody" colspan="2"><table class="tableStyle" id="tbl2" style='width:745px;'>
<tr>
<tr>
<td class="def_TH">Port</td>
<td class="def_TH spacer30Percent">Empfangene Bytes</td>
<td class="def_TH spacer30Percent">Gesendete Bytes</td>
<td class="def_TH spacer30Percent">Pakete mit CRC-Fehlern</td>


<tr class="portID" name="portID">
<td class="def firstCol" sel="text">1</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='00000000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='00000000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">2</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='0000000F6B990000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='000000C5C3FD0000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">3</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='0000001832370000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='00000082774F0000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">4</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='00000000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='00000000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">5</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='48CB0000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='00000011A4F00000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">6</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='0C600000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='FFE70000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">7</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='0000015754F10000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='000000277A1E0000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>

<tr class="portID" name="portID">
<td class="def firstCol" sel="text">8</td>
<td class="def" sel="text"></td>
<input type='hidden' name='rxPkt' value='00000000'>
<td class="def" sel="text"></td>
<input type='hidden' name='txpkt' value='00000000'>
<td class="def" sel="text"></td>
<input type='hidden' name='crcPkt' value='00000000'>


</tr>

</table>
</td></tr>
</table>
</td></tr>
</form>
<script>
var str = CreateButtons('button','Zähler zurücksetzen','submitClearCounters()','btn_Cancel','on');
str += CreateButtons('button','Aktualisieren','submitForm()','btn_Refresh','on');
PaintButtons(str);
</script>
</body>
</html>


