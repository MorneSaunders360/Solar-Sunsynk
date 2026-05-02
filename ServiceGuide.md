# Solar Service Sunsynk
# Service Mappings
1. This mapping gives an understanding of how the data in the JSON corresponds to the elements on the interface. 
# To Set System Mode
![image](https://github.com/MorneSaunders360/Solar-Sunsynk/assets/60499349/a43b349e-a8b5-47c6-8cc4-a834846bee78)

1. **Work Mode**:
    - JSON key: `"sysWorkMode"`
    - HTML Element: Radio buttons with labels "Selling First", "Zero-Export + Limit To Load Only", and "Limited to Home".
    - Value from JSON: `"sysWorkMode":"2"` which corresponds to the third radio button "Limited to Home".

2. **Solar Export**:
    - Doesn't have a direct JSON key in the provided JSON data.
    - HTML Element: Switch for "Solar Export".

3. **Use Timer**:
    - Doesn't have a direct JSON key in the provided JSON data.
    - HTML Element: Switch for "Use Timer".

4. **Max Sell Power**:
    - JSON key: `"pvMaxLimit"`
    - HTML Element: Input field labeled "Max Sell Power(0 ~ 9600W)".
    - Value from JSON: `"pvMaxLimit":"8000"`.

5. **Energy pattern**:
    - JSON key: `"energyMode"`
    - HTML Element: Radio buttons with labels "Priority Batt" and "Priority Load".
    - Value from JSON: `"energyMode":"0"` which corresponds to the "Priority Batt".

6. **Grid Trickle Feed**:
    - JSON key: `"zeroExportPower"`
    - HTML Element: Input field labeled "Grid Trickle Feed".
    - Value from JSON: `"zeroExportPower":"0"`.

7. **Time Configurations**:
    - There are multiple keys in the JSON for this:
      - `"sellTime1"`, `"sellTime2"`, ...: Represent the times.
      - `"sellTime1Pac"`, `"sellTime2Pac"`, ...: Represent the power at those times.
      - `"cap1"`, `"cap2"`, ...: Represent the battery state of charge (SOC) at those times.
    - HTML Elements: Inputs labeled "Time 1", "Power1(0 ~  9000W)", "Battery SOC1", and so on for other times.
    - Example Values from JSON: `"sellTime1":"01:00"`, `"sellTime1Pac":"8000"`, `"cap1":"55"`.

8. **Grid Charge**:
    - JSON keys: `"time1on"`, `"time2on"`, ... which seem to represent whether the times are active or not.
    - HTML Elements: Checkboxes labeled "Time 1", "Time 2", ...
    - Values from JSON: `"time1on":true`, `"time2on":"false"`, ...

9. **Gen Charge**:
    - JSON keys: `"genTime1on"`, `"genTime2on"`, ... similar to Grid Charge.
    - HTML Elements: Checkboxes under "Gen Charge".
    - Values from JSON: All seem to be `"false"`.
# To Set Battery Settings
![image](https://github.com/MorneSaunders360/Solar-Sunsynk/assets/60499349/ba3f7924-d67a-45f1-8025-6d1bcb8c6d82)

1. **Batt Type**:
    - JSON key: `"battMode"`
    - HTML Element: Radio buttons with labels "Lithium", "AGM V", "AGM %", and "No batt".
    - Value from JSON: `"battMode":"-1"` which corresponds to the first radio button "Lithium".

2. **Batt Capacity (0-9999Ah)**:
    - JSON key: `"batteryCap"`
    - HTML Element: Input field labeled "Batt Capacity (0-9999Ah)".
    - Value from JSON: `"batteryCap":"200"`.

3. **Discharge Amps**:
    - JSON key: `"batteryMaxCurrentDischarge"`
    - HTML Element: Input field labeled "Discharge Amps".
    - Value from JSON: `"batteryMaxCurrentDischarge":"140"`.

4. **Charge Amps**:
    - JSON key: `"batteryMaxCurrentCharge"`
    - HTML Element: Input field labeled "Charge Amps".
    - Value from JSON: `"batteryMaxCurrentCharge":"140"`.

5. **ShutDown (0-100%)**:
    - JSON key: `"batteryShutdownCap"`
    - HTML Element: Input field labeled "ShutDown (0-100%)".
    - Value from JSON: `"batteryShutdownCap":"10"`.

6. **Restart (0-100%)**:
    - JSON key: `"batteryRestartCap"`
    - HTML Element: Input field labeled "Restart (0-100%)".
    - Value from JSON: `"batteryRestartCap":"30"`.

7. **Low Batt (0-100%)**:
    - JSON key: `"batteryLowCap"`
    - HTML Element: Input field labeled "Low Batt (0-100%)".
    - Value from JSON: `"batteryLowCap":"25"`.

8. **Activate**:
    - JSON key: `"batteryOn"`
    - HTML Element: Switch labeled "Activate".
    - Value from JSON: `"batteryOn":"1"` (Switched On).

9. **BMS_Err_Stop**:
    - JSON key: `"bmsErrStop"`
    - HTML Element: Switch labeled "BMS_Err_Stop".
    - Value from JSON: `"bmsErrStop":"0"` (Switched Off).

10. **Protocol (0-20)**:
    - JSON key: `"lithiumMode"`
    - HTML Element: Input field labeled "Protocol (0-20)".
    - Value from JSON: `"lithiumMode":"0"`.

11. **Grid Charge**:
    - JSON key: `"sdChargeOn"`
    - HTML Element: Switch labeled "Grid Charge".
    - Value from JSON: `"sdChargeOn":"1"` (Switched On).

12. **Grid Start (10-90%)**:
    - JSON key: `"sdStartCap"`
    - HTML Element: Input field labeled "Grid Start (10-90%)".
    - Value from JSON: `"sdStartCap":"10"`.

13. **Grid Amps (0~275A)**:
    - JSON key: `"sdBatteryCurrent"`
    - HTML Element: Input field labeled "Grid Amps (0~275A)".
    - Value from JSON: `"sdBatteryCurrent":"40"`.

14. **Gen Charge**:
    - JSON key: `"genChargeOn"`
    - HTML Element: Switch labeled "Gen Charge".
    - Value from JSON: `"genChargeOn":"0"` (Switched Off).

15. **Grid Signal**:
    - JSON key: `"gridSignal"`
    - HTML Element: Switch labeled "Grid Signal".
    - Value from JSON: `"gridSignal":"0"` (Switched Off).

16. **Gen Signal**:
    - JSON key: `"genSignal"`
    - HTML Element: Switch labeled "Gen Signal".
    - Value from JSON: `"genSignal":"0"` (Switched Off).

17. **Gen Force**:
    - JSON key: `"generatorForcedStart"`
    - HTML Element: Switch labeled "Gen Force".
    - Value from JSON: `"generatorForcedStart":"0"` (Switched Off).

18. **Batt Empty V (41-63V)**:
    - JSON key: `"batteryEmptyV"`
    - HTML Element: Input field labeled "Batt Empty V (41-63V)".
    - Value from JSON: `"batteryEmptyV":"45"`.

19. **Signal ISLAND MODE**:
    - JSON key: `"signalIslandModeEnable"`
    - HTML Element: Switch labeled "Signal ISLAND MODE".
    - Value from JSON: `"signalIslandModeEnable":"0"` (Switched Off).

20. **Low Power Mode<Low Batt**:
    - JSON key: `"lowPowerMode"`
    - HTML Element: Switch labeled "Low Power Mode<Low Batt".
    - Value from JSON: `"lowPowerMode":"0"` (Switched Off).

21. **Disable Float Charge**:
    - JSON key: `"disableFloatCharge"`
    - HTML Element: Switch labeled "Disable Float Charge".
    - Value from JSON: `"disableFloatCharge":"0"` (Switched Off).

22. **Low Noise Mode**:
    - JSON key: `"lowNoiseMode"`
    - HTML Element: Switch labeled "Low Noise Mode".
    - Value from JSON: `"lowNoiseMode":"8000"`.

# To Set Auxiliary Load
![image](https://github.com/MorneSaunders360/Solar-Sunsynk/assets/60499349/e5ac0fc3-2387-43ec-be4b-068237e42131)

1. **SmartLoad Setup (Radio Buttons)**:
    - JSON key: `"loadMode"`
    - HTML Element: Radio buttons with labels "Gen Input", "Aux Load Output", and "For Micro Inverter Input".
    - Value from JSON: `"loadMode":"0"` which corresponds to the first radio button "Gen Input".

2. **Gen peak-shaving (Switch)**:
    - JSON key: `"genPeakShaving"`
    - HTML Element: Switch labeled "Gen peak-shaving".
    - Value from JSON: `"genPeakShaving":"0"` (Switched Off).

3. **Gen peak-shaving power (500 ~ 30000W)**:
    - JSON key: `"genPeakPower"`
    - HTML Element: Input field labeled "Gen peak-shaving power(500 ~ 30000W)".
    - Value from JSON: `"genPeakPower":"8000"`.

4. **OFF % (0-100%)**:
    - JSON key: `"genOffCap"`
    - HTML Element: Input field labeled "OFF % (0-100%)".
    - Value from JSON: `"genOffCap":"95"`.

5. **ON % (0-100%)**:
    - JSON key: `"genOnCap"`
    - HTML Element: Input field labeled "ON %(0-100%)".
    - Value from JSON: `"genOnCap":"100"`.

6. **GEN connect to Grid input (Switch)**:
    - JSON key: `"genConnectGrid"`
    - HTML Element: Switch labeled "GEN connect to Grid input".
    - Value from JSON: `"genConnectGrid":"1"` (Switched On).

7. **AC couple on load side (Switch)**:
    - JSON key: `"acCoupleOnLoadSideEnable"`
    - HTML Element: Switch labeled "AC couple on load side".
    - Value from JSON: `"acCoupleOnLoadSideEnable":"0"` (Switched Off).

8. **AC couple on grid side (Switch)**:
    - JSON key: `"acCoupleOnGridSideEnable"`
    - HTML Element: Switch labeled "AC couple on grid side".
    - Value from JSON: `"acCoupleOnGridSideEnable":"0"` (Switched Off).

9. **Generator minimum solar power**:
    - JSON key: `"genMinSolar"`
    - Value from JSON: `"genMinSolar":"500"`.

10. **Generator OFF voltage**:
    - JSON key: `"genOffVolt"`
    - Value from JSON: `"genOffVolt":"51"`.

11. **Generator ON voltage**:
    - JSON key: `"genOnVolt"`
    - Value from JSON: `"genOnVolt":"54"`.

12. **Grid always on**:
    - JSON key: `"gridAlwaysOn"`
    - Value from JSON: `"gridAlwaysOn":"0"` (Switched Off).

13. **Off-grid immediately off**:
    - JSON key: `"offGridImmediatelyOff"`
    - Value from JSON: `"offGridImmediatelyOff":"0"` (Switched Off).

14. **AC couple upper frequency**:
    - JSON key: `"acCoupleFreqUpper"`
    - Value from JSON: `"acCoupleFreqUpper":"52"`.
  
# To Set Basic Settings
![image](https://github.com/MorneSaunders360/Solar-Sunsynk/assets/60499349/fd62f60d-3b97-45cf-90dc-1e2a7a736d1b)

1. **Time Syncs (Switch)**:
    - JSON key: `"timeSync"`
    - HTML Element: Switch labeled "Time Syncs".
    - Value from JSON: `"timeSync":"1"` (Switched On, as indicated by the `is-checked` class).

2. **Beeper On/Off (Switch)**:
    - JSON key: `"beep"`
    - HTML Element: Switch labeled "Beeper On/Off".
    - Value from JSON: `"beep":"0"` (Switched Off).

3. **AM/PM (Switch)**:
    - JSON key: `"ampm"`
    - HTML Element: Switch labeled "AM/PM".
    - Value from JSON: `"ampm":"0"` (Switched Off).

4. **Lock out all changes (Switch)**:
    - JSON key: `"lockOutChange"`
    - HTML Element: Switch labeled "Lock out all changes".
    - Value from JSON: `"lockOutChange":"0"` (Switched Off).

5. **Auto Dim Sec (Switch)**:
    - JSON key: `"autoDim"`
    - HTML Element: Switch labeled "Auto Dim Sec".
    - Value from JSON: `"autoDim":"1"` (Switched On, as indicated by the `is-checked` class).

# To Set Advanced Settings
![image](https://github.com/MorneSaunders360/Solar-Sunsynk/assets/60499349/296b1adc-b716-4545-9e40-ad8a5c7c4bd4)

1. **Parallel (Switch)**:
    - JSON key: `"parallel"`
    - HTML Element: Switch labeled "Parallel".
    - Value from JSON: `"parallel":"0"` (Switched Off).

2. **Equipment mode (Radio)**:
    - JSON key: `"equipMode"`
    - HTML Element: Radios labeled "Master" and "Slave".
    - Value from JSON: `"equipMode":"0"` (Slave is checked).

3. **Modbus SN (Input)**:
    - JSON key: `"modbusSn"`
    - HTML Element: Input with label "Modbus SN (0-16)".
    - Value from JSON: `"modbusSn":"0"`

4. **Phase (Radio)**:
    - JSON key: `"phase"`
    - HTML Element: Radios labeled "A", "B", "C".
    - Value from JSON: `"phase":"0"` (A is checked).

5. **CT ratio (Input)**:
    - JSON key: `"externalCtRatio"`
    - HTML Element: Input with label "CT ratio".
    - Value from JSON: `"externalCtRatio":"2000"`

6. **Meter Select (Dropdown)**:
    - JSON key: `"meterSelect"`
    - HTML Element: Dropdown with label "Meter Select".
    - Value from JSON: `"meterSelect":"0"` (No Meter is selected).

7. **Grid side INV Meter2 (Switch)**:
    - JSON key: `"gridSideINVMeter2"`
    - HTML Element: Switch labeled "Grid side INV Meter2".
    - Value from JSON: `"gridSideINVMeter2":"0"` (Switched Off).

8. **Max Solar Power (Input)**:
    - JSON key: `"solarMaxSellPower"`
    - HTML Element: Input with label "Max Solar Power(1000 ~ 12000W)".
    - Value from JSON: `"solarMaxSellPower":"9000"`

# To Set Grid Settings

1. **Grid peak-shaving (Switch)**:
    - JSON key: `"gridPeakShaving"`
    - Value from JSON: `"gridPeakShaving":"0"` (Switched Off).

2. **Grid peak-shaving power**:
    - JSON key: `"gridPeakPower"`
    - Value from JSON: `"gridPeakPower":"8000"`.

3. **Parallel and equipment settings**:
    - JSON keys: `"parallel"`, `"equipMode"`, `"modbusSn"`, `"phase"`.
    - Example values from JSON: `"parallel":"0"`, `"equipMode":"0"`, `"modbusSn":"0"`, `"phase":"2"`.

4. **Meter and CT settings**:
    - JSON keys: `"meterSelect"`, `"gridSideINVMeter2"`, `"exMeterCtSwitch"`, `"meterA"`, `"meterB"`, `"meterC"`, `"smartCTEnable"`, `"exMeterCT"`.
    - Example values from JSON: `"meterSelect":"0"`, `"gridSideINVMeter2":"0"`, `"smartCTEnable":"0"`.

5. **Generator and grid behavior**:
    - JSON keys: `"genPeakShaving"`, `"genPeakPower"`, `"genConnectGrid"`, `"genToLoad"`, `"gridAlwaysOn"`, `"micExportGridOff"`.
    - Example values from JSON: `"genPeakShaving":"0"`, `"genPeakPower":"8000"`, `"genConnectGrid":"1"`.

6. **Protection and lock settings**:
    - JSON keys: `"sensorsCheck"`, `"remoteLock"`, `"bmsErrStop"`, `"atsEnable"`, `"atsSwitch"`, `"drmEnable"`, `"backupDelay"`, `"signalIslandModeEnable"`, `"isletProtect"`.
    - Example values from JSON: `"sensorsCheck":"-1"`, `"remoteLock":"0"`, `"bmsErrStop":"0"`.

7. **Solar and MPPT settings**:
    - JSON keys: `"solarMaxSellPower"`, `"solar1WindInputEnable"`, `"solar2WindInputEnable"`, `"solar3WindInputEnable"`, `"solar2WindInputEn"`, `"solar3WindInputEn"`, `"mpptMulti"`, `"pv1SelfCheck"`, `"pv2SelfCheck"`, `"pv3SelfCheck"`.
    - Example values from JSON: `"solarMaxSellPower":"9000"`, `"mpptMulti":"1"`, `"pv2SelfCheck":"1"`.

8. **Voltage and current curve settings**:
    - JSON keys: `"volt1"` through `"volt12"` and `"current1"` through `"current12"`.
    - These correspond to the advanced voltage/current values shown on the Grid Settings page.

9. **Additional grid payload flags**:
    - JSON keys: `"acOutputPowerLimit"`, `"risoEn"`, `"pwm"`, `"nightPowerSave"`, `"earthBond"`, `"codeMode"`, `"smartMeter2Enable"`, `"tenOverVoltEn"`, `"tenOverVoltVal"`, `"arcFactFrz"`.
    - Example values from JSON: `"acOutputPowerLimit":"1"`, `"pwm":"0"`, `"arcFactFrz":"-2143004677"`.
