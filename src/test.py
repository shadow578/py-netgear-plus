import py_netgear_plus	

#sw = py_netgear_plus.NetgearSwitchConnector("192.168.123.11", "SE@Nienhaus!53")

sw = py_netgear_plus.NetgearSwitchConnector("192.168.0.239", "SW@Nienhaus!53")
sw.autodetect_model()
print(sw.get_login_cookie())

data = sw.get_switch_infos()
print(sw.switch_model.MODEL_NAME)

ok = sw.reboot()
print(ok)
