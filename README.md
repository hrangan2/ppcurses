# ppcurses
![screenshot](/screenshot.png?raw=true)

## Usage

Clone and install the package
```
$ git clone git@github.com:hrangan2/ppcurses.git
$ pip install -e ppcurses
```

Add a bit of configuration to `~/.secrets/keys`
```
$ cat ~/.ppcurses/config
[ppcli]
token={{PROJECTPLACE_ACCESS_TOKEN}}
domain=api-service.projectplace.com
```

Run ppcurses
```
$ ppcurses
```
