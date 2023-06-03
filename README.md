# Solar Sunsynk ![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

A Home Assistant integration to track your sunsynk solar system.

![image](https://user-images.githubusercontent.com/109594480/233388451-6bad6329-64bc-42e0-b4e9-e63eb1ae4978.png)

# HACS Install 
1. Access HACS: Open Home Assistant and click on HACS in the sidebar.
2. Go to Integrations: Navigate to the Integrations tab.
3. Add Custom Repository: Click on the menu in the top right corner (three vertical dots), then select Custom Repositories.
4. Enter Details: In the new window, you need to input the necessary information about the custom integration you want to add
5. Add custom repository URL: Paste the URL of the repository you want to add.
6. Select category: Choose 'Integration' from the category dropdown menu.
7. Add: Click the Add button to confirm. This action should add the custom integration to HACS.
8. Select "+ Explore & Download Repositories" and search for "Solar Sunsynk"
9. Select "Solar Sunsynk" and "Download this repository with HACS"
10. Once downloaded, go to settings, then devices and services
11. Click on add intergration and search for 'Solar Sunsynk'
12. Follow the prompt with user name and then password, wait for 2 minutes and your data should be loaded

13. Setup cards and automations

# Sensor
 Go to developer tool thne select the states tab. Then filter the entities by searching for solar and you will be able to see all the sensors available.
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
