# pyEDPac

## installation of latest (github) version

### using requirements.txt

pip install -r requirements

## All the required files for running a simulation are in examples/

### Full runs:

- run_evo.py : the full simulation
- run_evo_novisu.py : same, no graphics

### Testing

- test_evo.py : A limited version of the simulation
- test_evo_novisu.py : same, no graphics

### Testing:

```bash
python run_evo.py --stats_path test_stats
```



## Previous versions

Versions exist as .zip releases

### v0.1 (~Original EDPac)

- go to /home/INT/meunier.d/Téléchargements/pyEDPac-0.1.zip
- download zip
- extract (unzip) pyEDPac-0.1.zip


```bash
cd pyEDPac-0.1/examples
python run_population.py
```


### v0.2 (MultiPac 2D)

- go to /home/INT/meunier.d/Téléchargements/pyEDPac-0.2.zip
- download zip
- extract (unzip) pyEDPac-0.2.zip

```bash
cd pyEDPac-0.2/examples
python run_evo.py --stats_path run_multipac
```
