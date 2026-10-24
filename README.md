# Philippine TVET Statistics: National Accomplishment on Assessment and Certification

A data analytics project analyzing the national accomplishment of Technical-Vocational Education and Training (TVET) assessment and certification in the Philippines for January 2021. The project transforms raw government data into a structured PostgreSQL database, performs analytical queries using SQL, and presents key findings through an interactive Streamlit dashboard.

## Objectives

1. Clean and prepare the original dataset for reliable analysis.
2. Document data-cleaning decisions, including the handling of missing values, duplicate records, inconsistent formats, and data types.
3. Store the cleaned data in a relational PostgreSQL database.
4. Use SQL queries to investigate regional and provincial assessment and certification outcomes.
5. Develop an interactive dashboard with geographic filters, visualizations, key performance indicators, and analytical findings.
6. Deploy the dashboard using Streamlit Community Cloud.

## Dataset

**Source:** Technical Education and Skills Development Authority (TESDA)

**Dataset:** *Number of Persons Assessed and Certified, January 1–31, 2021*

**Reporting period:** January 1–31, 2021

The dataset contains reported assessment and certification statistics across Philippine regions and provinces, including:

- Number of assessed persons by sex
- Total number of persons assessed
- Number of certified persons by sex
- Total number of persons certified
- Reported certification rate
- Geographic classifications, including region and province

The original workbook is processed before loading into the database. 

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data cleaning, transformation, and processing |
| Pandas | Data manipulation and analysis |
| Jupyter Notebook | Exploratory data analysis and documentation of cleaning decisions |
| PostgreSQL | Relational database and analytical queries |
| Neon | Hosted PostgreSQL database |
| SQL | Data aggregation, ranking, and analytical querying |
| Streamlit | Interactive dashboard development |
| Plotly Express | Interactive charts and visualizations |
| SQLAlchemy | Python-to-PostgreSQL database connection |
| Git and GitHub | Version control and project repository |
| Streamlit Community Cloud | Dashboard deployment |

## Data Analytics Workflow

### 1. Data Cleaning and Preparation
The cleaning process addresses:

- Multi-row or inconsistent column headers
- Region labels that need to be associated with their corresponding provincial records
- Numeric data types for assessment and certification counts
- Consistency of reported certification-rate values
- Duplicate records and missing values
- Zero-valued and other exceptional records that require validation
- Separation of provincial records from subtotal or aggregate rows, where applicable

### 2. Relational Database Design
The cleaned data is loaded into a PostgreSQL database hosted on Neon.

The database separates geographic reference information from province-level statistics.

**`regions`**

Stores region identifiers, region codes, and region names.

**`province_stats`**

Stores provincial assessment and certification statistics, linked to the corresponding region and reporting period.


### 3. SQL Analysis

SQL queries are used to explore assessment and certification outcomes across geographic areas.
The project includes five questions:
1. Which regions and provinces recorded the highest assessment and certification counts?
2. How do assessment and certification totals compare across regions?
3. Which provinces have the highest and lowest reported certification rates?
4. How do assessment and certification counts differ by sex?
5. How much does each region or province contribute to the overall reported totals?

### 4. Interactive Dashboard

The Streamlit dashboard provides a visual summary of the dataset and allows users to explore results by geographic area.

**Key performance indicators**
- Total persons assessed
- Total persons certified
- Derived overall certification rate
- Number of provinces included in the current selection

**Visualizations**
- Assessment and certification counts by region
- Assessment and certification counts by province
- Reported certification rates by province
- Assessment and certification counts by sex

**Interactive features**
- Region filter with checkbox selection
- Province filter with checkbox selection dependent on the selected regions
- Automatic updates to metrics, charts, and key findings
- Expandable underlying data table
- Downloadable filtered dataset in CSV format

### 5. Key Findings

The dashboard dynamically summarizes the selected geographic data, including:

- Provinces with the highest assessment counts
- Provinces with the highest certification counts
- Provinces with the lowest reported certification rates among those with assessments
- Provinces with the highest reported certification rates among those with assessments

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- Git
- A Neon PostgreSQL database
- A GitHub account for repository hosting and deployment

### 1. Clone the Repository

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements file should include the packages used by the application, such as Streamlit, Pandas, Plotly, SQLAlchemy, `psycopg2-binary`, and `python-dotenv`.

### 4. Configure the Database Connection

### 5. Deployment

## Limitations
- The dataset represents a specific reporting period: January 2021. It should not be interpreted as a current or longitudinal picture of TVET outcomes.
- Findings depend on the completeness, definitions, and reporting practices of the original TESDA dataset.
- Reported certification rates and rates derived from aggregated totals may differ.
- The data describes assessment and certification counts; it does not, by itself, establish the causes of regional differences or measure long-term employment outcomes.
- Zero-valued and missing records require interpretation based on the source documentation rather than assumptions.

## Future Improvements
- Comparing assessment and certification outcomes across additional reporting periods
- Adding historical trend visualizations
- Incorporating more detailed TVET program or qualification classifications when data is available
- Improving automated data validation and refresh workflows
- Expanding analytical insights while preserving the original source's reporting definitions

Data source: **Technical Education and Skills Development Authority (TESDA), Philippines.**

This project was developed for educational and data analytics purposes ONLY. Results should be interpreted in the context of the source dataset and its reporting period.
