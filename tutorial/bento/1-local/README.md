# BentoML tutorial, part 1 - simple YOLOv5 service

In this tutorial, we will use the BentoML tutorial on object recognition. Instead of a traditional approach, we will start with implementing a simple system, and then demonstrate how easy it is to break it. In the next tutorial, we will implement routines to prevent the system from breaking, including using `schema-overseer`.

Overall, we want to demonstrate downsides of bad coding practices, and show good ones. As a foundation, we took the BentoML tutorial from
https://docs.bentoml.org/en/latest/quickstarts/deploy-a-yolo-model-with-bentoml.html


# Code

## Setup the project

We need to create the virtual environment and install necessary packages, listed in `requirements.txt`. Go to the tutorial folder `1-local` and run the following commands:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Download the YOLOv5 model and export it into BentoML model store

We will use the same model from the original BentoML tutorial. Run the following code to download the YOLOv5 model. It will occupy around 15MB.

```bash
python download_model.py
```

EXPORT model with custom objects


## Custom Runner for YOLOv5

We change this part from the original to have a configurable Runner, that uses YAML config files. We also trying to be smart by providing default values if the config doesn't contain fields.

## Bento service

```bash
bentoml serve service.py:svc
```

Go to http://0.0.0.0:3000/, upload the image. Use the `render` endpoint to get a picture with object boxes.


# How to use configs

- directly pass


# How can we break this system?

Now to the most interesting part - let's break the system. What could go potentially wrong with it? We will discuss several scenarios and risks associated with it. Then we will run the service to see how the system behaves in risky cases.

## "Old code - old model" and "new code - new model"

Works fine

## Old code - new model

Scenario - you built Bento using the new ML model but without updating your current code. The training team changed the model and updated the config, but they didn't tell the production team.

- You simply don't have a implementation for processing new models with new configs  - we inform you that a new scheme standard is out.

## New code - old model

You changed the production code, but you linked the old model that worked great previously. But the config is new, and it expects new config fields and values (config == custom_objects)





### Forgetting to update the custom_objects

scenario
update the config file - whatever

risk

how our system will behave
-> code with output

not updated config file ->

You simply forgot to supply the updated config files. In our case we were smart and supplied default values for config file. Additionally, when building a Docker container, you probably list the config file you want to put into Docker. However, if you test locally or everything is on the same server, you could get completely different results.

### Adding a new parameter

You want to add a new parameter - you need to change everything, and you could make a mistake, e.g., supply a wrong parameter name, that you won't catch because of the "get" method with a default value.

## New fornmat ML model with a novel config for it

### Adding a new config for a new model to production

Writing it from scratch and selecting what model it is - always need to rewrite lots of code

### One config for each model - copying and pasting code

New config - copy and paste

### Create one big config for several models

Get one big config


## Other risk - changing parameter values or any other shit - unexpected format

Changing parameter values in the config. If you have the same config values and just change parameters, you would expect, that evetything will go smoothly. There are several risks still. First, type conversion. Second, invalid parameter value.

This thing could be fixed by Pydantic

Pydantic can fix the compatability with Unions - but there are two problems - huge Unions and hard to extend, because the two layers are not isolated from each other. No sync