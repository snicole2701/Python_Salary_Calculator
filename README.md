# Salary Calculator Microservices Backend Development

## Overview
This project comprises three distinct microservices, working together to provide a comprehensive salary calculator application. Each microservice plays a specific role in the workflow, and they collectively handle user input, tax calculations, and final salary computation. The project also includes a test to trigger Microservice 1, testing seamless integration between the components.

## Microservices Breakdown
### Microservice 1: User Input Service
Purpose:
- Receives user-provided data related to income before deductions, date and age.

Key Features:
- API endpoint (/get-user-input) to fetch user input data.
- Validates the structure and content of user input.
- Ensures proper data formatting before sending the information downstream.

Interaction:
- Microservice 1 serves as the starting point of the workflow. It gathers input and sends it to Microservice 3 for initial calculations.

### Microservice 2: Tax Table Service
Purpose:
- Handles tax and rebate data by querying structured tax tables for calculations.

Key Features:
- Includes web scraping functionality to fetch the latest tax table data from the SARS website
- Pre-created SQLite databases containing tax brackets and rebate information for multiple financial years.
- Dynamic querying of tax brackets based on effective dates and user-provided income details.
- Robust endpoints (/get-tax-details) to handle tax and rebate queries, returning applicable data for calculations.

Future-Proof Design:
- Includes modular and maintainable code that simplifies future tax table updates.

### Microservice 3: Calculation Service
Purpose:
- Performs all calculations based on input data from Microservice 1 and tax data from Microservice 2.

Key Features:
- Initial calculations (perform_initial_calculations) based on user-provided data (e.g., total income, projected annual income).
- Sends intermediate calculation results to Microservice 2 and retrieves tax and rebate information.
- Final calculations (perform_final_calculations) include:- Tax calculations with and without bonuses/leave.
- UIF contributions and total deductions.
- Net salary computation.

Detailed logging for transparency at each stage.

Output:
- Returns formatted results

### Test Script
Trigger Microservice 1
Purpose:
- Verifies the workflow by triggering Microservice 1 and validating its functionality.

Script: 
trigger_microservice1.py
- Sends a request to Microservice 1's endpoint (/get-user-input).
- Prints the response to confirm that user input is correctly received and formatted.
- Logs errors or unexpected responses for debugging.

How to Run the Test:
- Ensure that Microservice 1 is running and accessible.
- Execute the script:python trigger_microservice1.py
- Observe the output to confirm successful communication with Microservice 1.

## Setup and Deployment
### Prerequisites
- Python
- Required libraries specified in the requirements.txt file.
- SQLite databases (tax_database.db and rebate_database.db).

### Environment Variables
Configure the following environment variables for deployment:
Microservice 1:
- PORT: Port number (e.g., 5000).

Microservice 2:
- TAX_DB_URI: Path to the tax_database.db file.
- REBATE_DB_URI: Path to the rebate_database.db file.
- PORT: Port number (e.g., 5001).

Microservice 3:
- USER_INPUT_SERVICE_BASE_URL: URL of Microservice 1.
- TAX_TABLE_SERVICE_BASE_URL: URL of Microservice 2.
- PORT: Port number (e.g., 5002).

### Deployment
- Deploy each microservice on a hosting platform such as Render.
- Ensure that database files are included in the deployment for Microservice 2.

## Workflow
Microservice 1: Accepts user input and sends it to Microservice 3.

Microservice 3: Performs initial calculations and forwards the results to Microservice 2 for tax and rebate data.

Microservice 2: Queries tax tables and returns the relevant data to Microservice 3.

Microservice 3: Completes final calculations and returns detailed results.

# Future Enhancements
- Store user monthly data in a database for more accurate calculations based on year to date incomes instead of a single month in 
