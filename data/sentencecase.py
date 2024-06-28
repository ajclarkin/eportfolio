import pandas as pd

# Read the CSV file
df = pd.read_csv('fields.csv')

# Convert the 'label' column to sentence case
df['label'] = df['label'].str.lower().str.capitalize()

# Reset the indexing on filed_id
df = df.reset_index(drop=True)
df['field_id'] = df.index + 1


# Save the modified DataFrame back to CSV
df.to_csv('fields.csv', index=False)

