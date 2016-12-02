from zashel.signal import MetaSignal

ConnectSignal = MetaSignal("Connect", ("uuid", "timeout"), (str, str))
DisconnectSignal = MetaSignal("Disconnect", ("uuid", ), (str, ))
