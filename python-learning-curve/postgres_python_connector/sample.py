import psycopg

# Connection details (replace with your own)
DATABASE_URL = "postgresql://inventory@localhost:5432/house_inventory_db"

def read_items():
  with psycopg.connect(DATABASE_URL) as conn:
   with conn.cursor() as cur:
       # Execute a command: create datacamp_courses table
       cur.execute("""CREATE TABLE house_inventory(
                  classifier varchar(20) PRIMARY KEY),
                  category char(20),
                  reference_link TEXT,
                  bedrooms FLOAT,
                  area FLOAT,
                  locality TEXT,
                  description TEXT,
                  address TEXT,
                  price FLOAT,
                  monthly_charges FLOAT,
                  cadastral_income FLOAT,
                  available_date TEXT,
                  origin TEXT;""")
       # Make the changes to the database persistent
       # cur.commit()
       print("created table")
       cur.execute("SELECT * FROM house_inventory")
       print("Executed")
       return cur.fetchall() # Fetch all results as a list of tuples

read_items()