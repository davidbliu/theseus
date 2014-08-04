Theseus
=======

Docker container management framework built on top of Marathon

## Explanation
Theseus is a lightweight framework to control marathon, making it easy for developers to deploy and keep track of containers.
It handles __namespacing__ (services and labeled groups) and __basic scheduling tasks__ (rolling update, restarting killed tasks on previous host, custom constraints)
The ship of Theseus is a thought experiment: if a ship has all its components replaced, is it still the same ship? Theseus will keep your Dockerized services running even if all the component containers are in flux.

## Getting started
1. fill out mesos.yaml with marathon host and ip, etcd host and ip, and subscriber host and ip
2. create config file with what applications you want to create, update, or destroy (example: added_configuration.yaml)
3. deploy applications 
 * python orchestrator.py ((config_file_path))
4. viewer
 * python viewer.py
 * localhost:5001

## In Progress
* monitoring container performance + metrics
* log rolling -> viewing
* machine-centric view (what processes are running on what machines etc)
