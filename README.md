# Whitez Mythic Plus
pulls infomation about Mythic Plus runs from a custom list of wow players via Raider.io and Battle.net API.

## how to setup
- in the folder "lists" create a file named "mains.txt" and "alts.txt" 
- fill this lists with WOW players that are listed at Raider.io (player-realm) without brackets
- if u have python3 and all imports ur good to go.

## usage
- the script only takes 1 argument. ( main.py *output_file* )
- if u want to get the Dungeon intime timer u need to use Battle.net API
- I personally run this on my WebServer every 5 min and write the output to my Apache2 (/var/www/html/index.html)

## specials notes
- in *players.txt* and *alts.txt* u can write #, to skip this line or write ! to get this player info, but not add him to the table
- in the folder "json" the script will create a json file with all pulled player information, include players with ! (format *'YYYY-MM-DD.json'*)
- u can use a proxy server to get the API requests

## setup Battle.net API
- go to Battle.net and get ur ClientID and ClientSecret
- add this in 2 lines to a file named 'bnetkeys'*<br>clientID<br>clientSecret*

## Proxy and Login
- if u want to use a proxy or a rnd proxy to make the requests, just add a file in the folder "lists" with the name "proxy.txt"
- in that file write only the IP's of the proxys. One ip per line (it must be HTTPS proxys and listen to port 8080)
- for the login create a file called 'proxykey' and write in it just one line *user:password*

# About Me
I'm not a programmer @all and don't work in the IT sector. For me this is just a hobby.
I build this kind of Website just for me and my Frieds to keep track of our WoW progress over the actual addon.
With this Site we can find out pretty quickly who needs a Keystone at a certain Level and how many runs u have done this week or is an alt missing some m+ runs.
