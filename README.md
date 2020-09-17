# Cache Timings

Just some basic python scripts to automate the process of timing a cache optimised
problems.

## Installation
```console
user@linux:~$ python setup.py
```

## Usage
On the test machine first compile the `C` code then run the `test_blocksize.py`

```console
user@linux: python test_blocksize.py
```

This will run several timed iterations of the `bench_block` program and push it to a Google
Firebase project. This includes uploading graph images and raw data.

```console
uaer@linux:~$ python data.py
```
This does data manipulations to the completed data sets, like plotting speed to the L2 and L3
cache sizes.

## Author
Jos Craw <jos@joscraw.net>
