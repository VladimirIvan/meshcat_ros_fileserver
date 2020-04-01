# Meshcat ROS FileServer
This script creates a basic file server for mesh, texture and configuration files used by ROS.

Usage:
```
meshcat-ros-fileserver [-h] [--file-root [FILE_ROOT]] [--port [PORT]] [--origin [ORIGIN]]
```

Example:
```
meshcat-ros-fileserver -f /
```
to expose file at any location on the system (potential security issue) or:
```
meshcat-ros-fileserver -f ${PWD}
```
to expose only files relative to the current directory.
The files can be accessd at `http://127.0.0.1:9000/files/` plus the file path, e.g.:
```
http://127.0.0.1:9000/files//opt/ros/melodic/share/rviz/images/splash.png
```

Only supported file extensions will be served (printed when the script starts). Other file types will be filtered out.

Default port is 9000. The `origin` enables file requests from different IP/port than the one on which the Meshcat is running. It is set to `*`, enabling requests from anywhere. For higher security set this to another value (see CORS Access-Control-Allow-Origin header settings).

