from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection setup
TAX_DB_URI = os.getenv("TAX_DB_URI", "sqlite:///tax_database.db")
REBATE_DB_URI = os.getenv("REBATE_DB_URI", "sqlite:///rebate_database.db")
USER_INPUT_SERVICE_BASE_URL = os.getenv("USER_INPUT_SERVICE_BASE_URL", "https://salary-calculator-user-input.onrender.com")
CALCULATION_SERVICE_BASE_URL = os.getenv("CALCULATION_SERVICE_BASE_URL", "https://salary-calculator-calculation-service.onrender.com")

# Validate environment variables
if not TAX_DB_URI or not REBATE_DB_URI:
    raise ValueError("Environment variables TAX_DB_URI and REBATE_DB_URI must be set.")

logger.info(f"TAX_DB_URI: {TAX_DB_URI}")
logger.info(f"REBATE_DB_URI: {REBATE_DB_URI}")
logger.info(f"USER_INPUT_SERVICE_BASE_URL: {USER_INPUT_SERVICE_BASE_URL}")
logger.info(f"CALCULATION_SERVICE_BASE_URL: {CALCULATION_SERVICE_BASE_URL}")

# Create database engines
try:
    tax_engine = create_engine(TAX_DB_URI, future=True)
    rebate_engine = create_engine(REBATE_DB_URI, future=True)
    # Test database connections
    with tax_engine.connect() as conn:
        logger.info("Successfully connected to tax database.")
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        logger.info(f"Tax database tables: {[table[0] for table in tables]}")
    with rebate_engine.connect() as conn:
        logger.info("Successfully connected to rebate database.")
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        logger.info(f"Rebate database tables: {[table[0] for table in tables]}")
except Exception as e:
    logger.error(f"Error creating database engines: {e}")
    raise

# Root route
@app.route("/", methods=["GET"])
def home():
    """Welcome route for the service."""
    return "Welcome to the Tax Table Service!", 200

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "OK"}), 200

@app.route("/get-tax-details", methods=["POST"])
def get_tax_details():
    """
    Fetch applicable tax details and rebate details.
    """
    logger.info("Accessing /get-tax-details route")
    data = request.json

    # Debug user input data
    logger.info(f"Received data: {data}")

    try:
        # Validate required inputs
        month = data.get("month")
        year = data.get("year")
        age_group = data.get("age_group")
        projected_annual_income_excluding_bonus_leave = data.get("projected_annual_income_excluding_bonus_leave")
        projected_annual_income_plus_bonus_leave = data.get("projected_annual_income_plus_bonus_leave")

        if not all([month, year, age_group, projected_annual_income_excluding_bonus_leave, projected_annual_income_plus_bonus_leave]):
            logger.error("Missing required input fields")
            return jsonify({"error": "Missing required input fields"}), 400

        # Determine the applicable tax period table
        user_date = datetime(year, month, 1).date()
        table_name = find_applicable_table(user_date)
        if not table_name:
            return jsonify({"error": "No applicable tax period table found"}), 404

        # Query tax data for projected annual income excluding bonus and leave pay
        tax_data_income = query_tax_data(table_name, projected_annual_income_excluding_bonus_leave)
        if not tax_data_income:
            return jsonify({"error": "No tax data found for projected_annual_income"}), 404

        # Query tax data for projected annual income plus bonus leave
        tax_data_bonus = query_tax_data(table_name, projected_annual_income_plus_bonus_leave)
        if not tax_data_bonus:
            return jsonify({"error": "No tax data found for projected_annual_income_plus_bonus_leave"}), 404

        # Query rebate data 
        rebate_data = query_rebate_data(age_group, year)
        if not rebate_data:
            return jsonify({"error": "No rebate data found"}), 404

        # Combine results
        response_data = {
            "tax_data_income": tax_data_income,
            "tax_data_bonus": tax_data_bonus,
            "rebate_value": rebate_data
        }
        return jsonify({"message": "Tax details fetched successfully", "data": response_data}), 200

    except Exception as e:
        logger.error(f"Error in /get-tax-details: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

def find_applicable_table(user_date):
    """
    Finds the applicable tax period table based on the user-provided date.
    """
    try:
        with tax_engine.connect() as conn:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            result = conn.execute(text(query)).fetchall()
            table_names = [row[0] for row in result]

            for table_name in table_names:
                # Filter relevant tables
                if not table_name.startswith("tax_period_"):
                    continue

                # Query for effective_date and end_date
                query = f"SELECT effective_date, end_date FROM {table_name} LIMIT 1;"
                row = conn.execute(text(query)).fetchone()

                if row:
                    effective_date = datetime.strptime(row[0], "%Y-%m-%d").date()
                    end_date = datetime.strptime(row[1], "%Y-%m-%d").date()

                    if effective_date <= user_date <= end_date:
                        logger.info(f"Applicable table found: {table_name}")
                        return table_name
            logger.warning("No applicable tax period table found.")
            return None
    except Exception as e:
        logger.error(f"Error finding applicable table: {e}")
        return None

def query_tax_data(table_name, income):
    """
    Queries tax data from the applicable table for a given income.
    """
    try:
        with tax_engine.connect() as conn:
            query = f"""
            SELECT min_income, max_income, tax_on_previous_bracket, tax_percentage
            FROM {table_name}
            WHERE min_income <= :income AND max_income >= :income;
            """
            row = conn.execute(text(query), {"income": income}).fetchone()
            if row:
                return {
                    "min_income": row[0],
                    "max_income": row[1],
                    "tax_on_previous_bracket": row[2],
                    "tax_percentage": row[3]
                }
            return None
    except Exception as e:
        logger.error(f"Error querying tax data: {e}")
        return None

def query_rebate_data(age_group, year):
    """
    Queries rebate data based on age grou and financial year
    """
    try:
        with rebate_engine.connect() as conn:
            query = """
            SELECT rebate_amount
            FROM rebate_table
            WHERE age_group = :age_group AND year = :year
            """  # Adjust condition if needed based on requirements
            row = conn.execute(text(query), {"age_group": age_group, "year": year}).fetchone()
            if row:
                return row[0]
            logger.warning(f"No rebate data found for age_group: {age_group}, year: {year}")
            return None
    except Exception as e:
        logger.error(f"Error querying rebate data: {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting Flask app")
    app.run(host="0.0.0.0", port=5001)