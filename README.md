Theseus
=======

Docker container management framework built on top of Marathon

## Explanation
Theseus is a lightweight framework to control marathon, making it easy for developers to deploy and keep track of containers.
It handles __namespacing__ (services and labeled groups) and __basic scheduling tasks__ (rolling update, restarting killed tasks on previous host, custom constraints)
The ship of Theseus is a thought experiment: if a ship has all its components replaced, is it still the same ship? Theseus will keep your Dockerized services running even if all the component containers are in flux.

### motivation for theseus
marathon is not the ideal container-friendly interface for deploying and organizing dockerized applications. 
it has concepts of apps and tasks but doesn't explicitly support services and groups. Therefore, a lightweight framework on top of marathon 
to handle these tasks provides a robust way to manage docker containers. Since marathon is in flux and will soon accommodate namespacing and 
even scheduling tasks like rolling updates, this framework is even more crucial. instead of changing how developers interface with marathon 
you can simply update your framework (theseus) according to the changes in marathon. this allows you to keep the interface to your cluster 
the same even with changes to marathon.

## Getting started
1. fill out mesos.yaml with marathon host and ip, etcd host and ip, and subscriber host and ip
2. create config file with what applications you want to create, update, or destroy (example: added_configuration.yaml)
3. deploy applications 
 * `python orchestrator.py {{config_file_path}}`
4. viewer
 * python viewer.py
 * localhost:5001

## Example Configuration

* deploy 
  * deploys new apps. if the labeled group is already deployed, theseus will perform a rolling update
  * if you are only adding instances, theseus will just add instances for you
  * specify app name
  * labels are required
  * image is required
  * the following are optional (see example)
  * ports, environment, instances, cpu, mem, constraints, custom-constraints (only fixed-host available)
  

```yaml
deploy:
  ingestor:
    image: 54.189.193.228:5000/flask
    ports: 
      ssh: 22
      api: 5000
    environment:
      APP_NAME: Ingestor
      KEYSPACE_NAME: 'flask_keyspace2'
      TABLE_NAME: 'flask_table2'
    instances: 4
    cpus: 0.1 
    mem: 128
    labels: ['dev']
```

* remove
  * undeploy a group and remove it from etcd
  * specify app name and labels

```yaml
remove:
  ingestor:
    image: 54.189.193.228:5000/flask
    labels: ['dev']
```

## In Progress
* monitoring container performance + metrics
* log rolling -> viewing
* machine-centric view (what processes are running on what machines etc)
