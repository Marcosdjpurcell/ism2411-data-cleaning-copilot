# Reflection on Copilot usage

During this project I used GitHub Copilot to generate initial code for several helper functions. Specifically, I used Copilot to suggest the implementations for `load_data` and `clean_column_names`. I prompted Copilot by writing clear comments above each function describing the purpose, inputs, and expected behavior. Copilot provided reasonable starting code which I then reviewed and modified.

What Copilot generated
Copilot initially produced basic implementations that read CSV files and applied simple string operations to column names. The auto-generated code included good structure but lacked error handling and did not drop fully empty rows. I accepted the suggestions and adjusted them.

What I modified
For `load_data` I added a try/except to handle encoding errors and ensured fully-empty rows are dropped. For `clean_column_names` I tightened the regular expression to also remove punctuation and replaced sequences of whitespace with underscores. I renamed some variables to be more descriptive and added an additional helper to strip whitespace from likely text columns. These changes were necessary to meet the assignment requirements and to make the script robust on messy data.

What I learned
I learned that Copilot is useful for scaffolding common tasks quickly (loading data, basic string cleaning) but that human oversight is necessary for edge cases: encoding problems, missing-value policies, and ensuring numeric conversions work. For example, Copilot suggested conversion of price to numeric but didn’t suggest a consistent policy for missing values; I chose to fill price with median and quantity with 0 to keep behavior consistent. Overall, Copilot speeds development but a careful human review is essential to produce production-ready code.
