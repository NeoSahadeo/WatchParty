## Prerequisites

You will need to install `uv` and install the packages.

## Running the server

Update the `src/main.py` base_dir path to the location where you want to serve
videos from.

```
python -m src.main
```

### Forward

Port: 8000

## Generating a room

Run the module with `python -m src.db`. Press `enter` or type `help` to see
possible commands.

To create a room:

```
WatchParty Database Manager:
>
Commands:
  insert 			             Interactive room creation
  insert [ROOM_ID] [PASSWORD] 	 Create a permenant room
  delete [ROOM_ID] 		         Delete a permenant room
  list 				             List room ids

> insert
ROOM ID [leave blank to auto generate]:
Password: Password1234
Inserted successfully
Room ID: ac431a
Password: Password1234
```

Remember the password, you won't see it again.

`ctrl+c` to exit
