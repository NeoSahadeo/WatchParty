## Running the frontend

1. Intall the packages with `pnpm i`
2. Build the server `pnpm build`
3. Create .env and add IP's
4. Run the server with `node build`

## .env

Specify both a public and local ip. If you don't plan on port forwarding just
stub in the value with `0.0.0.0`

```
PUBLIC_IP=130.123.120.220
PUBLIC_LOCAL_IP=10.10.10.172
```


To specify a port on Linux

```
PORT=4173 node build
```
