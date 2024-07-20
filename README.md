# MLOps Project for Road Accidents

This project aims to reduce the number of road accidents by identifying high-risk areas and providing recommendations to improve safety. The data used in this project consists of annual files from 2005 to 2022, containing information about the characteristics, locations, vehicles, and users involved in accidents.

## Project Organization

    ├── LICENSE
    ├── README.md           <- The top-level README for developers using this project.
    ├── .github
    │   └── workflows
    │       └── ci-cd.yaml  <- GitHub Actions workflow for CI/CD.
    ├── data
    │   ├── external        <- Data from third party sources.
    │   ├── interim         <- Intermediate data that has been transformed.
    │   ├── processed       <- The final, canonical data sets for modeling.
    │   └── raw             <- The original, immutable data dump.
    ├── docker
    │   ├── Dockerfile      <- Dockerfile for building the application container.
    │   └── docker-compose.yml <- Docker Compose file to setup the entire application stack.
    ├── logs                <- Logs from training and predicting.
    ├── models              <- Trained and serialized models, model predictions, or model summaries.
    │   ├── trained_model.joblib <- Example of a trained model file.
    │   └── model_evaluation.txt <- Evaluation metrics of the trained model.
    ├── notebooks           <- Jupyter notebooks.
    │   └── 1.0-ldj-initial-data-exploration.ipynb
    ├── references          <- Data dictionaries, manuals, and all other explanatory materials.
    ├── reports             <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures         <- Generated graphics and figures to be used in reporting.
    ├── requirements.txt    <- The requirements file for reproducing the analysis environment.
    ├── setup.py            <- Makes the project pip installable (pip install -e .).
    └── src                 <- Source code for use in this project.
        ├── __init__.py     <- Makes src a Python module.
        ├── api             <- FastAPI application for the model.
        │   ├── main.py     <- Main file to run the FastAPI application.
        │   ├── predict.py  <- Endpoint for making predictions.
        │   ├── train.py    <- Endpoint for training the model.
        │   └── utils.py    <- Utility functions for the API.
        ├── config          <- Configuration files for the project.
        │   └── config.yaml <- Configuration parameters for training and prediction.
        ├── data            <- Scripts to download or generate data.
        │   ├── check_structure.py <- Script to check file and folder structure.
        │   ├── import_raw_data.py <- Script to import raw data from a source.
        │   └── make_dataset.py    <- Script to process raw data into final dataset.
        ├── features        <- Scripts to turn raw data into features for modeling.
        │   └── build_features.py  <- Script to build features.
        ├── models          <- Scripts to train models and then use trained models to make predictions.
        │   ├── train_model.py <- Script to train the model.
        │   ├── predict_model.py <- Script to make predictions with the trained model.
        │   └── test_features.json <- Example input for the predict_model script.
        ├── tests           <- Unit tests and integration tests.
        │   ├── test_data.py <- Tests for data processing.
        │   ├── test_features.py <- Tests for feature engineering.
        │   ├── test_models.py <- Tests for model training and prediction.
        │   ├── test_api.py  <- Tests for API endpoints.
        │   └── test_endpoints.py <- Tests for API endpoints.
        └── visualization   <- Scripts to create exploratory and results oriented visualizations.
            └── visualize.py <- Script to create visualizations.

## Getting Started

### Prerequisites

- Python 3.8
- Docker
- Docker Compose

### Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/your_username/mlops_accidents.git
    cd mlops_accidents
    ```

2. **Create and activate a virtual environment**:

    ```sh
    python -m venv my_env
    my_env\Scripts\activate
    ```

3. **Install the dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

### Usage

1. **Import raw data**:

    ```sh
    python src\data\import_raw_data.py
    ```

2. **Process data to create the final dataset**:
    ***Initializing ./data/raw as input file path and ./data/preprocessed as output file path.***

    ```sh
    python src\data\make_dataset.py
    ```

3. **Train the model**:

    ```sh
    python src\models\train_model.py
    ```

4. **Run the FastAPI application**:

    ```sh
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    ```

### Docker

1. **Build and start the Docker containers**:

    ```sh
    docker-compose up --build
    ```

2. **Stop and remove the Docker containers**:

    ```sh
    docker-compose down
    ```

### Running Tests

1. **Run all tests**:

    ```sh
    pytest
    ```

### CI/CD with GitHub Actions

This project uses GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). The configuration file is located at `.github/workflows/ci-cd.yaml`.

### Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m 'Add my feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a Pull Request.

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgements

This project is based on the MLOps practices and aims to provide a robust and scalable solution for road accident analysis and prediction.