Theseus
=======

Docker container management framework built on top of Marathon

## Explanation
Theseus is a lightweight framework to control marathon, making it easy for developers to deploy and keep track of containers.
The ship of Theseus is a thought experiment: if a ship has all its components replaced, is it still the same ship? Theseus will keep your Dockerized services running even if all the component containers are in flux.

## Getting started
1. fill out mesos.yaml with marathon host and ip, etcd host and ip, and subscriber host and ip
2. run python app.py from the root directory
3. use web ui at localhost:5000 to control containers
  * deploy new containers with deploy button 
  * need to provide declarative specification for container. an example is given in configuration.yaml
  * services can be scaled, updated, replaced, tagged with different labels
  * query for services or labels with inputs at top

## In Progress
* monitoring container performance + metrics
* log rolling -> viewing
