import requests

# URL for the first microservice's user input endpoint
USER_INPUT_URL = "https://salary-calculator-user-input.onrender.com/add-user-input"

# Sample user input data to trigger the workflow
user_input_data = {
    "month": 1,  # January
    "year": 2024,
    "age": 30,  # User's age
    "basic_salary": 35000,  # Monthly basic salary
    "commission": 5000,     # Commission earned
    "bonus": 2000,          # Bonus amount
    "overtime": 1000,       # Overtime payment
    "leave_pay": 500,       # Leave pay
}

def send_user_input():
    """
    Function to send user input data to Microservice 1 and trigger the workflow.
    """
    try:
        print("Sending user input to Microservice 1...")
        
        # Make the POST request to the /add-user-input endpoint
        response = requests.post(USER_INPUT_URL, json=user_input_data)

        # Handle the response
        if response.status_code == 200:
            print("✅ User input successfully sent!")
            print("Response from Microservice 1:", response.json())
        elif response.status_code == 400:
            print("❌ Error: Invalid user input data.")
            print("Response:", response.text)
        elif response.status_code == 500:
            print("❌ Error: Internal server error in Microservice 1.")
            print("Response:", response.text)
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print("Response:", response.text)
    except requests.RequestException as e:
        print(f"❌ Failed to connect to Microservice 1: {e}")

if __name__ == "__main__":
    send_user_input()