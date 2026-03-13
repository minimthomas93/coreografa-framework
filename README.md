# Coreógrafa – Directed Comparative Fuzz Testing Framework for Functionally Equivalent Systems.

## Files to run specific targets are included in seperate folders under: 
Coreografa/src/evaluation

- Coreografa/src/evaluation/all-in-one  - This folder was created to make our code more generic to all the subjects.
- Coreografa/src/evaluation/regex       - Working folder for regex (In Progress)
- Coreografa/src/evaluation/searching   - Working folder for search functions. (Haven't touched for long)
- Coreografa/src/evaluation/sorting     - Working folder for search functions. (Haven't touched for long)
- Coreografa/src/evaluation/sql         - Working folder for sql functions. Working fine except a plotting error.
- Coreografa/src/evaluation/viability   - This was created some time before based on our discussion regarding viability. Ignore it.
- Coreografa/src/evaluation/weasyrprint - Working folder for weasyprint functions. (Haven't touched for long)
- Coreografa/src/evaluation/xml         - First draft folder for xml. Ignore it.
- Coreografa/src/evaluation/xml_test    - Latest working folder with all the latest updates. USE IT FOR TEST.

## Output Files: 
- Inputs will be added to Coreografa/src/inputs
- Main summaries will be added to Coreografa/src/main_summary/main_summary.csv
- JSON requests will be added to Coreografa/src/requests/
- Newly generated grammar files will be added to Coreografa/src/new_grammar_files/
- Individual summaries will be added to Coreografa/src/individual_summary/
- Plots will be added to Coreografa/src/evaluation/<subject_folder>/plots

## To run a subject

1. Create a virtual environment - .venv\Scripts\Activate.ps1

Example: 

<img width="433" height="41" alt="image" src="https://github.com/user-attachments/assets/06b4ac80-a235-4cdc-a9cf-f3e066d6568d" />

2. Go to the respective folder - 

Example:

<img width="607" height="108" alt="image" src="https://github.com/user-attachments/assets/6d37ded9-252d-48e1-b437-539b5edbd5fc" />

3. Run example.py file

<img width="609" height="82" alt="image" src="https://github.com/user-attachments/assets/cb32893a-be29-4e1b-8dc9-384068f6e9e1" />

Example Output:

<img width="604" height="245" alt="image" src="https://github.com/user-attachments/assets/e0241544-317f-4ef3-9b55-0ff2c0cda01c" />






