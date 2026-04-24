# to do

\- wifi

\- index.html (frontend)

\- node.js (api)

\- automatictly run the scripts (wifi, backend.py, server.py)



# components

\- buzzer (on fail/music on new high score)

\- rgb LED (on fail/success/connected)

\- joystick/d-pad (move the dot around)

\- Switch Button (isToggled, save/display drawings)

\- 8x8 led matrix:

&#x09;\* start = a dot apears and flashes at a random location of the matrix, the amount of dots = currrent round (ex.: round 5 = 5 dots)

&#x09;\* goal = using a joystick or directly on the web sites interface (right, left, up, down) to direct a dot to its previous location

&#x09;\* rules = dot always starts in the middle, target location will always be at least 2 squares from center

&#x09;\* ui = start game button, reset/debug button, end game button, able to draw on the matrix, game status, current round, score, difficulty modifier where the user chooses how many dots he will have to remember

&#x09;\* button1 = save current drawing

&#x09;\* button2 = display saved drawing

&#x09;\* extra = 2nd gamemode, memory leap frog (from lego party or squid games glass floor game)



# sudo nano /etc/systemd/system/memorytest.service

[Unit]
Description=Memory Tester Startup Service
After=network.target

Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'sudo systemctl restart dnsmasq && python3 /MemoryTest-app/backend.py && python3 /MemoryTest-app/server.py'
Restart=always
RestartSec=10   

[Install]
WantedBy=multi-user.target   