# Moda
This repo contains the backend code for the app MODA.

## STEPS to run the code:
  
0. (optional) If you want to run it on a VM, you first need to connect to it through ssh using:
```
ssh -i /path/to/private_key username@hostname_or_IP
```

1. Clone the repo:
```
git clone https://github.com/zaidmehdi/moda-backend.git
```
2. CD into the directory:
```
cd moda-backend/
```
3. Build the docker image:
```
docker build -t moda .
```
4. Run the docker image:
```
docker run moda
```
