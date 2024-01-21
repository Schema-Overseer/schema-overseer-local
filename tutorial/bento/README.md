# Use Schema Overseer for managing BentoML model configs

Use `schema-overseer` with BentoML framework for serving models as a Machine Learning models config manager. `schema-overseer` acts like a single source of truth and ensures that the MLOps production team always have configs with correct fields and their values for ML models from the ML development team.

Schema-overseer helps catch issues on the development stage, much earlier than production and even testing stage. It makes some errors catch-able on the build-time, and others – on the first launch. What are these bugs? They are generally about Machine Learning model configs - see next sections.

We embrace the concept of "fail-fast", as the speed of iterations in both software developmetn and machine learning are crucial. For more - see our list of principles.


## How tutorials are structured?

The tutorials are structured as step-by-step guides to build working Machine Learning serving applications, illustrating both good architectural principles and how to use `schema-overseer` to support them.

1. The first tutorial closely follows BentoML's object recognition tutorial but integrates Pydantic models. It emphasizes the importance of strict contracts, especially in scenarios like monorepositories and small teams. Two critical cases are explored: introducing a new ML model and updating the configuration for an existing model.

2. In the second tutorial, we introduce `schema-overseer` to address challenges arising from lax contract practices in both development and production stages. Learn how `schema-overseer` prevents your application from running with incorrect schemas, saving you from costly issues in the production stage, such as re-deploying the whole system.

3. ...

4. ...


# Schema Overseer for MLOps

## How people use "schemas" in MLOps?

"Schema" is a generic term, usually describing what an object looks like, what keys it has and what are the types and requirements for values for the keys. In MLOps, one of the most used schemas are configs:

1. Configs for Machine Learning model training – how to train them, when they were train, with what hyperparameters, and so on. Tools such as `MLFlow` or `DVC` are prime examples of saving configs for models. This is usually called "experiment tracking", and configs are helping reproduce experiments.

2. Configs for deployment of Machine Learning models – parameters for models and prepcrossing/postprocessing functions, as well as additional tags (`"cat_prediction:latest"`), labels (`"team:cat_team"` and `"stage:prod"`) and metadata (`"acc:0.775"` and `"dataset_version:20240103"`).

In these tutorials, we are focusing on MLOps. We will describe typical problems when managing different BentoML model configs for small and big teams, and how `schema-overseer` solves them.

## How to use Schema Overseer to resolve configs challenges in MLOps?

In the context of MLOps, managing and synchronizing configurations becomes paramount. `schema-overseer` acts as a guardian, ensuring that both development and production teams adhere to the same schema contracts, preventing potential issues and maintaining consistency across the ML pipeline.

### Schema Standardization and Synchronization

`schema-overseer` provides a robust solution for standardizing schemas and synchronizing them between development and production teams. It acts as a mediator, facilitating seamless communication and preventing misalignments caused by changes in model configurations.

### Error Prevention and Early Detection

By integrating `schema-overseer` into your workflow, you introduce an additional layer of protection. The service identifies discrepancies in schemas early on, preventing errors from propagating to the production stage. This proactive approach minimizes the chances of costly mistakes and enhances the reliability of your ML applications.

### Effortless Updates and Deployments

With `schema-overseer`, deploying new models or updating configurations becomes a streamlined process. The service ensures that both teams are on the same page, reducing the need for extensive communication and manual checks. This allows for agile development practices and facilitates continuous integration and deployment (CI/CD) workflows.


# Tutorials

The tutorial will consists of several parts, and the project will expand and be complex step-by-step. We will start from a simple case where you have a single repository and one-two Machine Learning team mebmers, responsible for both ML development and production. But soon, we will move from one repository and one team to several repositories and two teams – development and production. This allows us not only to clealy demonstrate how to build ML systems, but also allows users to pick up the level of complexity which suits their business needs. E.g., startup will be perfectly fine with the first two tutorials, focused on using `schema-overseer` locally. The larger and more mature teams will benefit the most from the first and third tutorials, with the third focused on using the `schema-overseer` as a separate service for schema standartization and synchronising across teams.

## List of tutorials

1. Basic one repository-small team use case, where we outline the Machine Learning and MLOps problems we solve, and what challenges there are with the ML model configs.

2. Local usage – for solo or small teams and single repository. `schema-overseer` works like an additional PIP package that ensures that you always use the correct schema.

3. Server usage – for several teams with different repositories. `schema-overseer` works as a service that synchronizes schemas between development and production teams, and prevents production teams from using wrong or incorrect schemas.


# Use case for the tutorial: object detection

For our tutorials, we will pick BentoML's example with YOLO model for our use case. The original tutorial is here: https://docs.bentoml.com/en/latest/quickstarts/deploy-a-yolo-model-with-bentoml.html The task of our service is to detect objects on the photo and return the list of objects with coordinates.

## Background

- The ML development team exports a BentoML model with some labels and metadata:

```
bentoml.pytorch.save_model(
    "cat_recognition",
    trained_model,
    labels={
        "owner": "cat_team",
        "stage": "dev",
    },
    metadata={
        "f1": f1_score,
        "dataset_version": "20210820",
    },
    custom_objects={
        "resize_resolution": (224, 224),
        "conf": 0.25,
        "multi_label": False
    }
)
```

- The production team uses the model metadata to save data points for monitoring the models, and uses the custom objects for preprocessing:

```
model = bentoml.pytorch.load_model("demo_mnist:latest")
```

- The key question is: how to ensure that the development and production team use the same model configs? What could go wrong? Usually, people write some `pydantic` code and have lots of checks of the upcoming model configs, which are extremely easy to miss. Let's consider two common cases and one advanced case, when everything could break.

## What could go wrong with configs?

In our use case, there is no communication between development and production teams except through GitHub or Slack. To get a new model up and running, a production team needs to check GitHub and ping the development team on Slack.

### Case 1: New Config for a New Model

The development team pushes a new model with a new schema, and doesn't notify the production team.

**Scenario:**
The expectation is the introduction of new parameters crucial for the model's functionality. However, without clear communication, the production team remains unaware of these changes, leading to potential issues as critical parameters might be missing.

**Impact:**
The absence of essential parameters could break the entire workflow, causing errors in data processing, model training, or inference.

### Case 2: New Version for the Old Config

The development team makes changes to an old schema, such as updating the model to work with data of a larger resolution without informing the production team. For instance, they shift from the original resolution of 224x224 to another resolution.

**Scenario:**
Changes in the schema, even subtle ones, can significantly impact the model's behavior. The production team, unaware of these modifications, might continue using outdated configurations, leading to unexpected results.

**Impact:**
Data mismatches due to resolution changes can introduce errors in model predictions, affecting the accuracy and reliability of the deployed models.

Other cases:
1. They dig into the data and realized, that confidence of 0.25 is too much for the business logic, and they want to find objects on images with much higher confidence, otherwise it is too much noise. They change the confidence values, but - surprise! - somebody decided that the `conf` parameter is too short, so they renamed it to `confidence`.

### Case 3 (Advanced): Deploy New Models Without Stopping the Service

In the current setup, deploying new models requires a complete overhaul, often referred to as a blue/green deployment.

**Scenario:**
When a new model is ready for deployment, the entire system must be brought down and replaced with the updated version. This process involves stopping the existing service, making the necessary changes, and then restarting it.

**Impact:**
This approach is resource-intensive, disrupts service availability during updates, and may introduce downtime, especially in scenarios where continuous service is crucial.


# Comparables

## Pydantic vs. Schema-Overseer

### Pydantic

- **Use Case:**
    - Pydantic is a powerful Python library for data validation and settings management, commonly used for defining data schemas in various applications.

- **Strengths:**
    - **Validation:** Pydantic excels in runtime data validation, ensuring that data adheres to the specified schema.
    - **Integration:** It seamlessly integrates with various Python frameworks and tools, making it a popular choice for developers.

- **Limitations:**
    - **Synchronization:** Pydantic alone does not provide mechanisms for schema synchronization across development and production teams.
    - **Centralized Management:** Managing schemas centrally and ensuring consistent usage across teams can be challenging.

### Schema-Overseer

- **Use Case:**
    - Schema-Overseer is specifically designed for managing and synchronizing data schemas, especially in the context of machine learning model configurations.

- **Strengths:**
    - **Centralized Schema Registry:** Provides a centralized repository for managing and versioning schemas, facilitating synchronization across teams.
    - **Prevention of Misalignments:** Acts as a guardian to prevent misalignments between development and production teams by enforcing schema contracts.

- **Advantages Over Pydantic Alone:**
    - **Synchronization:** Schema-Overseer addresses the challenges of schema synchronization, ensuring that both development and production teams use the same schema contracts.
    - **Error Prevention:** Proactively identifies discrepancies in schemas, preventing potential issues from reaching the production stage.

## Configuration Managers (Dynaconf, Omegaconf) vs. Schema-Overseer

### Configuration Managers

- **Use Case:**
    - Configuration managers, such as Dynaconf and Omegaconf, focus on handling application configurations, including settings, parameters, and environment variables.

- **Strengths:**
    - **Flexibility:** Configuration managers offer flexibility in handling various types of configurations for applications.
    - **Environment-Based Configuration:** They often provide support for managing configurations based on different environments (development, production, etc.).

- **Limitations:**
    - **Data Schema Management:** While they excel in managing application configurations, they may lack specialized features for handling and synchronizing complex data schemas.

### Schema-Overseer

- **Use Case:**
    - Schema-Overseer specializes in managing and synchronizing data schemas, particularly in the context of machine learning model configurations.

- **Strengths:**
    - **Dedicated Schema Management:** Focuses on the specific needs of managing machine learning model configurations and data schemas.
    - **Versioning and History:** Provides versioning capabilities, allowing teams to track changes to schemas over time.

- **Advantages Over Configuration Managers:**
    - **Specialized for ML Ops:** Schema-Overseer is tailored for MLOps scenarios, addressing challenges specific to machine learning model configurations.
    - **Integrated Synchronization:** Ensures seamless synchronization of schemas between development and production teams.

In summary, while Pydantic and configuration managers like Dynaconf and Omegaconf serve specific purposes well, Schema-Overseer offers specialized features for managing and synchronizing machine learning model configurations in MLOps scenarios.