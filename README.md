# Solar Sunsynk ![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

A Home Assistant integration to track your Sunsynk solar system.

![image](https://user-images.githubusercontent.com/109594480/233388451-6bad6329-64bc-42e0-b4e9-e63eb1ae4978.png)

# Features
1. Supports real-time monitoring of your Sunsynk solar system's parameters.
2. Allows you to adjust the settings of your system remotely through Home Assistant.
3. New: Now supports adjusting solar, battery, basic, auxiliary load, advanced, and grid settings remotely through the `set_solar_settings`, `set_battery_settings`, `set_basic_settings`, `set_auxiliary_load_settings`, `set_advanced_settings`, and `set_grid_settings` services.

# HACS Install

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MorneSaunders360&repository=Solar-Sunsynk&category=integration)

1. Access HACS: Open Home Assistant and click on HACS in the sidebar.
2. Go to Integrations: Navigate to the Integrations tab.
3. Add Custom Repository: Click on the menu in the top right corner (three vertical dots), then select Custom Repositories.
4. Enter Details: In the new window, you need to input the necessary information about the custom integration you want to add.
5. Add custom repository URL: Paste the URL of the repository you want to add.
6. Select category: Choose 'Integration' from the category dropdown menu.
7. Add: Click the Add button to confirm. This action should add the custom integration to HACS.
8. Select "+ Explore & Download Repositories" and search for "Solar Sunsynk".
9. Select "Solar Sunsynk" and "Download this repository with HACS".
10. Once downloaded, go to settings, then devices and services.
11. Click on add integration and search for 'Solar Sunsynk'.
12. Follow the prompt with user name and then password, wait for 2 minutes and your data should be loaded.
13. Setup cards and automations.

# Service Usage
1. To monitor your system, use the provided sensors in your Home Assistant dashboard.
2. Please guide for mapping service to sunsynk front end
https://github.com/MorneSaunders360/Solar-Sunsynk/blob/main/ServiceGuide.md
3. The editable controls are added to the main Sunsynk device as configuration entities. The very technical grid voltage/current curve controls are disabled by default and can be enabled from the entity registry if needed.
4. To adjust system settings, call the `solar_sunsynk.set_solar_settings` service with the desired parameters. For example:
```yaml
service: solar_sunsynk.set_solar_settings
data:
  sn: 2107269334
  safetyType: 2
  battMode: -1
  solarSell: 0
  pvMaxLimit: 8000
  energyMode: 0
  peakAndVallery: 1
  sysWorkMode: 2
  sellTime1: 01:00
  sellTime2: 05:00
  ...
```
5. To adjust battery settings, call the `solar_sunsynk.set_battery_settings` service with the desired parameters. For example:
```yaml
service: solar_sunsynk.set_battery_settings
data:
  sn: "2107269334"
  safetyType: "2"
  battMode: "-1"
  batteryCap: "200"
  batteryMaxCurrentCharge: "140"
  batteryMaxCurrentDischarge: "140"
  batteryShutdownCap: "10"
  batteryLowCap: "25"
  batteryRestartCap: "30"
  batteryOn: "1"
  lithiumMode: "0"
  sdChargeOn: "1"
  sdStartCap: "30"
  sdBatteryCurrent: "40"
  genChargeOn: "0"
  gridSignal: "0"
  generatorStartCap: "10"
  generatorBatteryCurrent: "40"
  absorptionVolt: "54"
  floatVolt: "54"
  sdStartVolt: "49"
  bmsErrStop: "0"
```
6. To adjust basic settings, call the `solar_sunsynk.set_basic_settings` service with the desired parameters. For example:
```yaml
service: solar_sunsynk.set_basic_settings
data:
  sn: "2107269334"
  timeSync: "1"
  beep: "0"
  ampm: "0"
  autoDim: "1"
  lockOutChange: "0"
```
7. To adjust auxiliary load settings, call the `solar_sunsynk.set_auxiliary_load_settings` service with the desired parameters. For example:
```yaml
service: solar_sunsynk.set_auxiliary_load_settings
data:
  sn: "2107269334"
  safetyType: "2"
  battMode: "-1"
  genMinSolar: "500"
  loadMode: "0"
  genOffCap: "95"
  genOnCap: "100"
  genOffVolt: "51"
  genOnVolt: "54"
  gridAlwaysOn: "0"
  offGridImmediatelyOff: "0"
  acCoupleFreqUpper: "52"
  genConnectGrid: "1"
  genPeakShaving: "0"
  genPeakPower: "8000"
  acCoupleOnLoadSideEnable: "0"
  acCoupleOnGridSideEnable: "0"
```
8. To adjust advanced settings, call the `solar_sunsynk.set_advanced_settings` service with the desired parameters. For example:
```yaml
service: solar_sunsynk.set_advanced_settings
data:
  sn: "2107269334"
  externalCtRatio: "2000"
```
9. To adjust grid settings, call the `solar_sunsynk.set_grid_settings` service with the desired parameters. For example:
```yaml
service: solar_sunsynk.set_grid_settings
data:
  sn: "2107269334"
  gridPeakShaving: "0"
  gridPeakPower: "8000"
  phase: "2"
  mpptMulti: "1"
  pv1SelfCheck: "0"
  pv2SelfCheck: "1"
  acOutputPowerLimit: "1"
```

# Sensors
 Go to developer tool, then select the states tab. Filter the entities by searching for solar and you will be able to see all the sensors available.
 ![image](https://user-images.githubusercontent.com/109594480/233350555-f44916c6-9522-4cb0-9994-9d195711cd99.png)
 
# Cards
I created these cards with the help the following
    
<details>
  <summary>Card 1</summary>

[Code](examples/card1.yaml)  
![image](https://user-images.githubusercontent.com/109594480/233350917-932c02d2-3e9d-4982-a589-47d440dafd3b.png)
</details>

<details>
  <summary>Card 2</summary>

[Code](examples/card2.yaml)  
![image](https://user-images.githubusercontent.com/109594480/233388223-9298c90e-aa48-45d3-9a07-3ed51ac25265.png)
</details>
