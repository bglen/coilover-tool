# coilover-tool

![Image of app window](/docs/app_picture.png)

Python tool for helping you set up coil-over suspension systems.

## Features
- Specify spring, damper body, damper shaft, and perch dimensions
- 3D visualization of the coilover throughout its travel range
- Calculate net spring rates with multiple springs
- Save and reopen human-readable project files (`.sus`)

## To Do
- Make projects vehicle specific and allow different coilover setups per vehicle corner
- Calculate ideal damping curves and requried adjustment for different spring options
- Add bump stop 3D geometry
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

## Project files
Projects are saved as JSON with the `.sus` extension so they stay easy to read and diff. Keys:
- `schema_version`: integer for future migrations (currently `1`)
- `unit` / `weight_unit`: `"mm"`/`"in"` and `"kg"`/`"lb"` representing the units shown in the UI when saved
- `slider`: integer 0–100 representing the travel slider position
- `inputs`: mapping of every numeric field by name to its displayed text value
- `toggles`: checkbox/radio states (helper/bump usage, perch options, flip damper)
- `corner`: which suspension corner was selected

Example:
```json
{
  "schema_version": 1,
  "unit": "mm",
  "weight_unit": "kg",
  "slider": 35,
  "inputs": {
    "spring_id": "63.5",
    "damper_free_length": "400",
    "corner_weight_front_left": "295"
  },
  "toggles": {
    "use_helper": false,
    "use_bump": true
  },
  "corner": "Front Left"
}
```
Use the File menu (New, Open…, Save, Save As…) to manage projects. If you type a filename without `.sus`, it is added automatically.

## Install
Clone the repository: `git clone https://github.com/bglen/coilover-tool`
   
Change directory into the repo: `cd your/path/to/repo`

Create a python virtual enviornment: `python3 -m venv .venv` 

Activate the virtual enviornment: `source .venv/bin/activate`

Install dependencies: `pip install -r requirements.txt`
   
Run the python script: `python coilover.py`
