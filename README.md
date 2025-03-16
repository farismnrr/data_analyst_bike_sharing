# Data Analysis of Bike Sharing Datasets

## Run via Docker
### Pull and Run Docker Image
```bash
docker run -d -p 8501:8501 --name streamlit-bike-sharing farismnrr/streamlit-bike-sharing
```

### Open Browser
Url: http://localhost:8501/

## Run via Manual
### Setup Environment - Anaconda

```bash
conda create --name streamlit-bike-sharing python=3.12
```

```bash	
conda activate streamlit-bike-sharing
```

```bash	
pip install -r requirements.txt
```
	
### Setup Environment - Shell/Terminal
```bash
mkdir Proyek-Analisis-Data-Dicoding
cd Proyek-Analisis-Data-Dicoding
```

```bash	
pipenv install
pipenv shell
```

```bash	
pip install -r requirements.txt
```

### Run streamlit app
```bash	
streamlit run dashboard.py
```

### Open Browser
Url: http://localhost:8501/