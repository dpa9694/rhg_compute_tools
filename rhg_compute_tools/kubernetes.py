# -*- coding: utf-8 -*-

"""Tools for interacting with kubernetes."""
import dask_kubernetes as dk
import dask.distributed as dd
import yaml as yml

def get_worker(name=None,extra_pip_packages=None, extra_conda_packages=None,
               memory_gb=11.5, nthreads=1, cpus=1.75,
               cred_path = '/opt/gcsfuse_tokens/rhg-data.json',
               env_items=None):
    """Start dask.kubernetes cluster and dask.distributed client to wrap 
    that cluster.
    
    Parameters
    ----------
    name (optional) : str
        Name of worker image to use. If None, default to worker specified in 
        `/home/jovyan/worker-template.yml`.
    extra_pip_packages (optional) : str
        Extra pip packages to install on worker. Syntax to install is 
        "pip install `extra_pip_packages`"
    extra_conda_packages (optional) :str
        Same as above except for conda
    memory_gb (optional) : float
        Memory to assign per 'group of workers', where a group consists of
        nthreads independent workers.
    nthreads (optional) : int
        Number of independent threads per group of workers. Not sure if this
        should ever be set to something other than 1.
    cpus (optional) : float
        Number of virtual CPUs to assign per 'group of workers'
    cred_path (optional) : str or None
        Path to Google Cloud credentials file to use. Defaults to rhg-data.json.
    env_items (optional) : list of dict
        A list of env variable 'name'-'value' pairs to append to the env variables
        included in worker-template.yml. (e.g. [{'name': 'GCLOUD_DEFAULT_TOKEN_FILE', 
        'value': '/opt/gcsfuse_tokens/rhg-data.json'}])
        
    Returns
    -------
    client : :py:class:dask.distributed.Client
    cluster : :py:class:dask_kubernetes.KubeCluster
    """

    with open('/home/jovyan/worker-template.yml', 'r') as f:
        template = yml.load(f)
    
    container = template['spec']['containers'][0]
    
    # replace the defualt image with the new one
    if name:
        container['image'] = name
    if extra_pip_packages is not None:
        container['env'].append({'name':'EXTRA_PIP_PACKAGES',
                                        'value':extra_pip_packages})
    if extra_conda_packages is not None:
        container['env'].append({'name':'EXTRA_CONDA_PACKAGES',
                                        'value':extra_conda_packages})
    if cred_path is not None:
        container['env'].append({'name': 'GCLOUD_DEFAULT_TOKEN_FILE',
                                 'value': cred_path})
    if env_items is not None:
        container['env'] = container['env'] + env_items
        
    ## adjust memory request
    # first in args
    args = container['args']
    nthreads_ix = args.index('--nthreads') + 1
    args[nthreads_ix] = str(nthreads)
    mem_ix = args.index('--memory-limit') + 1
    args[mem_ix] = '{}GB'.format(memory_gb)
    
    # then in resources
    resources = container['resources']
    limits = resources['limits']
    requests = resources['requests']
    limits['memory'] = '{}G'.format(memory_gb)
    limits['cpu'] = str(cpus)
    requests['memory'] = '{}G'.format(memory_gb)
    requests['cpu'] = str(cpus)

    
    ## start cluster and client and return
    cluster = dk.KubeCluster.from_dict(template)
    cluster

    client = dd.Client(cluster)
    client
    
    return client, cluster


