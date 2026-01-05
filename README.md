# coilover-tool

![Image of app window](/docs/app_picture.png)

Python tool for helping you set up coil-over suspension systems.

## Features
- Specify spring, damper body, damper shaft, and perch dimensions
- 3D visualization of the coilover throughout its travel range
- Calculate net spring rates with multiple springs

## To Do
- Add bump stop geometry
- Calculate and identify max travel condition: coil bind, bump stop engage, perch collison
- Calculate static ride position given corner weight, along with bump and droop travel ranges
- Option for flat spring ends
- Inverted damper option (mainly to visualize bump stop location)
- Flipped damper option (visualize body attatched to sprung mass)
- Add threaded perch ranges to estimate ride heigh adjustment range and corresponding bump and droop travel
- Geometry collisions (ex: helper spring perch collides with top of damper body before bump engagement)
- Option to add threaded sleeve geometry on to damper body (mainly for coilover conversions)
- Drop down list to select from Hypercoil spring catalog
- Other damper types (currently drawn as mcpherson / strut insert)
- Option for preload adjustment
- Calculate warnings for helper springs (fully compressed at full droop, loose main spring at some point through travel range)
- Lower sleeve geometry for independent ride height and preload
- option for bump spring instead of bump stop
- Graphs for spring rate vs damper travel
- Calculate ideal damping curves and requried adjustment for different spring options

## Install
Clone the repository: `git clone https://github.com/bglen/coilover-tool`
   
Change directory into the repo: `cd your/path/to/repo`

Create a python virtual enviornment: `python3 -m venv .venv` 

Activate the virtual enviornment: `source .venv/bin/activate`

Install dependencies: `pip install -r requirements.txt`
   
Run the python script: `python coilover.py`