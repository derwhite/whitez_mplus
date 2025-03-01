# Whitez Mythic Plus
Pulls infomation about Mythic Plus runs from a custom list of wow players via Raider.io and Battle.net API.

## how to setup
- in the folder "lists" create a file named "mains.txt" and "alts.txt" 
- fill this lists with WOW players that are listed at Raider.io (player-realm) without brackets
- if u have python3 and all imports ur good to go.

## usage
- the script only need one required argument. ( main.py *output_file* )
- if u want to get the Dungeon intime timer u need to use Battle.net API
- I personally run this on my WebServer every 5 min and write the output to my Apache2 (/var/www/html/index.html)

## specials notes
- in *players.txt* and *alts.txt* u can write #, to skip this line or write ! to get this player info, but not add him to the table
- in the folder "json" the script will create a json file with all pulled player information, include players with ! (format *'YYYY-MM-DD.json'*)
- u can use a proxy server to get the API requests

## setup Battle.net API
- go to Battle.net and get ur ClientID and ClientSecret
- add these values to `settings.conf` (without quotes etc.)
- Battle.net API requests are optional. 
  If you don't have an account, the script will still work. 
  The output page just doesn't show all the information.

## RaiderIO API Keys
- Raider.IO release a new feature for their public API. Now we can call up to 1000 API Calls / per min.
- I'm actually don't need that much calls, because i call only every few minutes a new build from the Data, but i implemented it anyway.
- go to http://raider.io/settings/apps and get your API Key.
- write that key in your `settings.conf` file under [rio] / rio_apikey = YOUR_API_KEY.
- Thats it.

# About Me
I'm not a programmer @all and don't work in the IT sector. For me this is just a hobby.
I build this kind of Website just for me and my Frieds to keep track of our WoW progress over the actual addon.
With this Site we can find out pretty quickly who needs a Keystone at a certain Level and how many runs u have done this week or is an alt missing some m+ runs.
