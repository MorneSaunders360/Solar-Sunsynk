# Solar Sunsynk ![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

A Home Assistant integration to track your Sunsynk solar system.

![image](https://user-images.githubusercontent.com/109594480/233388451-6bad6329-64bc-42e0-b4e9-e63eb1ae4978.png)

# Features
1. Supports real-time monitoring of your Sunsynk solar system's parameters.
2. Allows you to adjust the settings of your system remotely through Home Assistant.
3. New: Now supports adjusting solar settings remotely through the `set_solar_settings` service.

# HACS Install

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MorneSaunders360&repository=Solar-Sunsynk&category=plugin)

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
3. To adjust system settings, call the `solar_sunsynk.set_solar_settings` service with the desired parameters. For example:
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
