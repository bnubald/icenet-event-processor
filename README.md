# icenet-event-processor

## Overview

The IceNet event processing engine is part of the cloud infrastructure that allow subscription to activities, rule processing and common actions to be undertaken for the sake of project integrations.

## Detail

More to follow soon

### Building the image

Azure deployments collect the image automatically from the latest tag, you can build it thus (if you're me):

```
docker build -t jimcircadian/iceneteventprocessor:[[version]]
docker tag jimcircadian/iceneteventprocessor:[[version]] jimcircadian/iceneteventprocessor:latest
docker push jimcircadian/iceneteventprocessor:latest```
```


## Limitations

Communications service needs manually enabling to use destination services, with azurerm provider, once created.

## Development docs

Documentation I found useful during development: 

* https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli%2Cv1&pivots=programming-language-python
* https://www.docker.com/blog/speed-up-your-development-flow-with-these-dockerfile-best-practices/

## Licensing

Please review the LICENSE file for more information.

