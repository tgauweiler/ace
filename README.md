# Automated Cluster Execution

ACE is python script to create slurm jobs with different executable arguments based on a flexible configuration file.\
One usage is for example benchmarking code on a SLURM cluster with different run parameters.

## Requirements
- Python 3

## Installation
```
git clone https://github.com/tgauweiler/ace.git
cd ace
pip3 install --user -r requirements.txt
```

## Usage
Some example configuration files:
- [config_example.yaml](config_example.yaml)
- [config_example_echo.yaml](config_example_echo.yaml)

SLURM jobs get generated by running
```
python3 benchmark.py config_example.yaml
```
Based on the given value ranges inside the configuration file ACE generates all possibles combinations and creates for each combination a batch script and schedules a SLURM job with `sbatch`.