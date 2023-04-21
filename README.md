# Solar sunsynk ![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

A Home Assistant integration to track your sunsynk solar system.

![image](https://user-images.githubusercontent.com/109594480/233388451-6bad6329-64bc-42e0-b4e9-e63eb1ae4978.png)

# HACS Install 
1. Go to HACS Integrations on your Home Assitant instance
2. Select "+ Explore & Download Repositories" and search for "Solar Sunsynk"
3. Select "Solar Sunsynk" and "Download this repository with HACS"
4. Once downloaded, go to your configuration.yaml and add the following code
 ```bash
 solar_sunsynk:
  username: "YOUR_USERANME"
  password: "YOUR_PASSWORD"
```
6. Setup cards and automations

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
