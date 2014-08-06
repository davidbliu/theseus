Theseus
=======

Docker container management framework built on top of Marathon

<img src='http://1.bp.blogspot.com/-tWuvAq0dsDY/T5VAdqS8T1I/AAAAAAAAAJo/6OVlbTbLpsU/s1600/trireme.jpg' height=200></img>
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
__docker!__

1. `docker build` (you may be missing custom-marathon-python, in which case `git clone --recursive` the repo since its a submodule)
2. `docker run`
 * docker run -d -p 22000:22 -p 5000:5001 -e MARATHON_HOST=50.18.90.238 -e MARATHON_PORT=8080 -e ETCD_HOST_ADDRESS=50.18.90.238 54.189.193.228:5000/theseus
3. visit the viewer at `{{host}}:5000` to see what is running
4. deploy/updating/removing new apps
5. accepts post requests to `{{host}}:5000/deploy`
 * some examples
 * `curl -X POST -H "Content-Type: application/json" localhost:5000/deploy -d@config.json`

heres what config.json looks like: (you can use yaml->json)

```json
{
  "deploy": {
    "ingestor": {
      "image": "54.189.193.228:5000/tester",
      "ports": {
        "ssh": 22
      },
      "instances": 3,
      "cpus": 0.1,
      "mem": 128,
      "labels": [
        "monkey"
      ]
    }
  }
}
```

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
