from sqlalchemy import create_engine, Column, Integer, Float, Date, MetaData, Table
from datetime import datetime

# Database connection
db_path = 'tax_database.db'  # Create the database file inside the project folder
engine = create_engine(f'sqlite:///{db_path}')  # Connect to (or create) the database
metadata = MetaData()

def create_and_populate_tax_period_table(table_name, effective_date, end_date, financial_year, tax_data):
    """
    Creates and populates a tax period table in the database.
    Args:
        table_name (str): The name of the table to create (e.g., tax_period_<year>).
        effective_date (datetime.date): The effective date for the table.
        end_date (datetime.date): The end date for the table.
        financial_year (int): The financial year for the table.
        tax_data (list): The tax data to populate the table with.
    """
    # Define the tax period table schema
    table = Table(
        table_name, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('min_income', Integer, nullable=False),
        Column('max_income', Integer, nullable=False),
        Column('tax_on_previous_bracket', Float, nullable=False),
        Column('tax_percentage', Float, nullable=False),
        Column('effective_date', Date, nullable=False),
        Column('end_date', Date, nullable=False),
        Column('financial_year', Integer, nullable=False)
    )

    # Create the table
    metadata.create_all(engine)
    print(f"Table '{table_name}' created successfully!")

    # Add effective_date, end_date, and financial_year to each row in tax_data
    for entry in tax_data:
        entry['effective_date'] = effective_date
        entry['end_date'] = end_date
        entry['financial_year'] = financial_year

    # Insert data into the table
    with engine.connect() as conn:
        with conn.begin():  # Begin a transaction
            conn.execute(table.insert(), tax_data)
            print(f"Data committed into '{table_name}' successfully!")

if __name__ == "__main__":
    # Shared tax bracket data for all financial years
    tax_data = [
        {'min_income': 1, 'max_income': 237100, 'tax_on_previous_bracket': 0, 'tax_percentage': 18},
        {'min_income': 237101, 'max_income': 370500, 'tax_on_previous_bracket': 42678, 'tax_percentage': 26},
        {'min_income': 370501, 'max_income': 512800, 'tax_on_previous_bracket': 77362, 'tax_percentage': 31},
        {'min_income': 512801, 'max_income': 673000, 'tax_on_previous_bracket': 121475, 'tax_percentage': 36},
        {'min_income': 673001, 'max_income': 857900, 'tax_on_previous_bracket': 179147, 'tax_percentage': 39},
        {'min_income': 857901, 'max_income': 1817000, 'tax_on_previous_bracket': 251258, 'tax_percentage': 41},
        {'min_income': 1817001, 'max_income': 9999999999, 'tax_on_previous_bracket': 644489, 'tax_percentage': 45},
    ]

    # Create and populate tax_period_2024
    create_and_populate_tax_period_table(
        table_name='tax_period_2024',
        effective_date=datetime.strptime('2023-03-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2024-02-28', '%Y-%m-%d').date(),
        financial_year=2024,
        tax_data=tax_data
    )

    # Create and populate tax_period_2025
    create_and_populate_tax_period_table(
        table_name='tax_period_2025',
        effective_date=datetime.strptime('2024-03-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2025-02-28', '%Y-%m-%d').date(),
        financial_year=2025,
        tax_data=tax_data
    )

    # Create and populate tax_period_2026
    create_and_populate_tax_period_table(
        table_name='tax_period_2026',
        effective_date=datetime.strptime('2025-03-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2026-02-28', '%Y-%m-%d').date(),
        financial_year=2026,
        tax_data=tax_data
    )