# my-sreality

Use [Sreality](sreality.cz) to find an export estates in desired locations.

## Motivation

The portal Sreality is great tool to search for some estate. However, it quickly becomes painful when you look for specifics such distance to your parents, distance to work or infrastructure (water, sewage, gas) as the portal does not support using such criteria for search. Even more cumbersome is to catalogue and compare your findings. Therefore I made a tool that queries sreality using broad criteria, stores the results, scores each record according to our needs and then plots/prints the results.

## Instalation

It's not a package therefore clone the repo and install requirements:

```
git clone https://github.com/jaroslavknotek/my-sreality/
cd my-sreality
pip install -f requirements.txt
```

## Example

See [baraky.md] which

- queries sreality according to input parameters
- finds the nearest city (given by config, see below)
- calculates commute time (based on manually inserted time as idos is infamously hard to work with)
- scores the results according to price, commute time and technical state
- prints/plots results

## Config

The folder assets has two files:

- estate_score_map.json - maps technical state of the estate to a number
- stations.json - a list of station that we picked to live nearby (as we wish to commute by train)







