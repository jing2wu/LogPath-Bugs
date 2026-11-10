# ClassCastException in energy scan

- Issue: https://github.com/zsmartsystems/com.zsmartsystems.zigbee/issues/1306
- Opened by cdjackson on 2022-02-26, closed on 2022-03-03
- Labels: bug
- Fix commit: 18036b298c8c85efc52611110d7dab2481c61f55

## Report

In the event that a scan terminates without completing (which could happen if, for example, the serial port is closed during the scan), then there is a CCE thrown.

```
    java.lang.ClassCastException: com.zsmartsystems.zigbee.dongle.ember.ezsp.command.EzspStartScanResponse cannot be cast to com.zsmartsystems.zigbee.dongle.ember.ezsp.command.EzspScanCompleteHandler
        at com.zsmartsystems.zigbee.dongle.ember.EmberNcp.doEnergyScan(EmberNcp.java:1084)
```
