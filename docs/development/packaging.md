# Packaging

## Packaging into an executable

The project takes advantage of [PyInstaller](https://pyinstaller.readthedocs.io/) to package the application into an executable.

The output binary and all embedded dependencies is located into a subfolder named: `dist/GeotribuToolbelt_{version}_{operating-system}_Python{python-version}`.

### Windows

> Comply with [Windows development requirements](windows) before to run.

```powershell
# Generates MS Version Info
python .\builder\version_info_templater.py

# Generates MS Executable
python -O .\builder\pyinstaller_build_windows.py
```

To run it, double-click on the executable file (*.exe).

### Ubuntu

> Comply with [Ubuntu development requirements](ubuntu) before to run.

```bash
# Generates binary executable
python -O ./builder/pyinstaller_build_ubuntu.py
```

To run it, for example:

```bash
cd dist/
chmod u+x ./GeotribuToolbelt_*
./GeotribuToolbelt_0-19-1_Ubuntu22-04_64bit_Python3-10-6
```

----

## Docker

:::{note}
Image is meant to be used, not to develop. So, it does not contain side code: `docs`, `tests`, etc.  
If you need that, edit the `.dockerignore` file.
:::

### Requirements

- Docker >= 20.10

### Build

```sh
docker build --pull --rm -f "Dockerfile" -t geotribu-cli:latest "."
```

Plus avancé avec build-kit et du cache :

```sh
docker buildx create --name bldr-geotribu --driver docker-container --use
```

```sh
docker buildx build --pull --rm --file Dockerfile \
    --cache-from type=local,src=.cache/docker/geotribu/ \
    --cache-from type=registry,ref=ghcr.io/geotribu/ \
    --cache-to type=local,dest=.cache/docker/geotribu/,mode=max \
    --load \
    --platform linux/amd64 \
    --progress=plain \
    -t geotribu-cli:latest .
```

### Run within the container

Enter into the container and run commands interactively::

```sh
> docker run --rm -it geotribu-cli:latest
root@55c5de0191ee:/user/app# geotribu --version
0.23.1
```

Run the CLI directly from the container:

```sh
> docker run --rm geotribu-cli:latest --version
0.23.1
```

Attention cependant, les commandes aboutissant sur un prompt ne fonctionneront pas dans un conteneur sans l'option interactive (`-it`) puisqu'il n'y pas de terminal tty a

```sh
> docker run -it --rm geotribu-cli:latest sc -f article "title:qgis"

```
