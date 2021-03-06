# ppcurses
_An ncurses interface to boards and cards with vim style keybindings._

![screenshot](/screenshot.png?raw=true)

## Usage
```
$ git clone git@github.com:hrangan2/ppcurses.git
$ pip install ./ppcurses
$ ppcurses
```

## Commands
```
Navigate windows with the arrow keys or hjkl

?                   Help
q                   Quit
y                   Copy the direct link for a card
u                   Undo your last action
/                   Filter the current list
r                   Refresh the current window
R                   Refresh all windows
S                   Change the project and board selection
g                   Go to the top of a list
G                   Go to the bottom of a list
cc                  Create a new card
xx                  Delete a card
aa                  Add a co-assignee to a card
ac                  Add a new comment
ak                  Add a checklist item
et                  Change the title of the card
ed                  Change the description of the card
eo                  Change the owner/assignee of the card
el                  Change the label of the card
ep                  Change the points on a card
ek <n>              Edit a checklist item
ec <n>              Edit a comment
xa <n>              Remove a co-assignee from the card
xc <n>              Delete a comment
xk <n>              Delete a checklist item
tk <n>              Toggle a checklist item
pk <n>              Convert a checklist item to a card
mc                  Move the card to a different column
mp                  Move the card to a different activity
```

## Development
Add a new section to `~/.ppcurses/config` pointing to a different domain and set the `mode` variable in `ppcurses/__init__.py` to the section suffix.

For example if you want a development configuration, add a section named `ppcurses_dev` to `~/.ppcurses/config` and set `mode = 'dev'` in `ppcurses/__init__.py`

Each section gets its own sqlite db for data caching, so you can swap environments by just changing the `mode` variable in `ppcurses/__init__.py`.

If you think the cache is corrupted, you can delete the corresponding `.db` file in `~/.ppcurses`.
