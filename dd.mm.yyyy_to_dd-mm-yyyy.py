import re 

input_file_path = 'dump.sql'
output_file_path = 'updated_dump.sql'

def update_dates_in_sql(input_file, output_file, table_name):
    with open(input_file, 'r') as file:
        sql_content = file.read()

    date_pattern = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")

    def replace_date(match):
        day, month, year = match.groups()
        return f"{day}-{month}-{year}"

    updated_sql_content = re.sub(
        rf"(INSERT INTO `{table_name}`.*?VALUES.*?\()(.*?)(\);)",
        lambda m: m.group(1) + date_pattern.sub(replace_date, m.group(2)) + m.group(3),
        sql_content,
        flags=re.DOTALL
    )

    with open(output_file, 'w') as file:
        file.write(updated_sql_content)

update_dates_in_sql(input_file_path, output_file_path, "bis_dodis_dataBaseRendu_transformed_final")

output_file_path
