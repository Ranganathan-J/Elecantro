import pandas as pd

# Create sample data
data = {
    'text': [
        "This product is amazing! Highly recommend it.",
        "Great customer service, very responsive team.",
        "Product quality could be better for the price point.",
        "Excellent value for money, will buy again!",
        "Fast shipping and well packaged product.",
        "Good product but shipping was delayed.",
        "Outstanding quality and features.",
        "Customer support was very helpful with my issue.",
        "Product works as described, very satisfied.",
        "Would recommend to friends and family.",
        "Good value for budget-conscious shoppers.",
        "Premium quality worth the extra cost.",
        "Easy to use and setup.",
        "Received damaged item, customer support resolved quickly.",
        "Product exceeded my expectations in every way.",
        "Fast delivery and great communication.",
        "Will definitely purchase again.",
        "Good product but minor issues with documentation.",
        "Excellent build quality and materials.",
        "Helpful customer support team."
    ],
    'product_name': [
        "Premium Widget", "Premium Widget", "Budget Widget", "Premium Widget", "Budget Widget",
        "Budget Widget", "Premium Widget", "Premium Widget", "Budget Widget", "Premium Widget",
        "Budget Widget", "Premium Widget", "Premium Widget", "Budget Widget", "Premium Widget",
        "Budget Widget", "Premium Widget", "Budget Widget", "Premium Widget", "Budget Widget"
    ],
    'customer_name': [
        "John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Wilson",
        "Diana Prince", "Eve Davis", "Frank Miller", "Grace Lee", "Henry Wilson",
        "Ivy Chen", "Jack Brown", "Kate Davis", "Liam Miller", "Mia Wilson",
        "Noah Chen", "Olivia Brown", "Parker Lee", "Quinn Davis", "Ruby Wilson"
    ],
    'customer_email': [
        "john@example.com", "jane@example.com", "bob@example.com", "alice@example.com", "charlie@example.com",
        "diana@example.com", "eve@example.com", "frank@example.com", "grace@example.com", "henry@example.com",
        "ivy@example.com", "jack@example.com", "kate@example.com", "liam@example.com", "mia@example.com",
        "noah@example.com", "olivia@example.com", "parker@example.com", "quinn@example.com", "ruby@example.com"
    ],
    'rating': [5, 4, 3, 5, 4, 2, 5, 4, 5, 5, 4, 5, 5, 3, 5, 4, 5, 3, 5, 4]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('sample_feedback_data.xlsx', index=False, engine='openpyxl')

print("Excel file created successfully!")
