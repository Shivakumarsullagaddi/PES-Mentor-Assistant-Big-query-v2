import os
import pandas as pd
from google.cloud import bigquery
import difflib
import traceback
from dotenv import load_dotenv
from typing import Optional


current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../.env")
load_dotenv(dotenv_path=env_path)

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET = os.getenv("DATASET_ID")
TABLE = os.getenv("TABLE_ID")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

try:
    client = bigquery.Client(project=PROJECT_ID, location="US")
except Exception as e:
    print(f"[ERROR] Failed to initialize BigQuery: {e}")

def mentor_exact_filter(campus: Optional[str] = None, department: Optional[str] = None) -> str:
    """Lists professors filtered by 'campus', 'department', or BOTH at the same time."""
    print(f"\n[DEBUG] === TOOL: mentor_exact_filter ===")
    print(f"[DEBUG] Filters Requested -> Campus: {campus} | Department: {department}")
    
    conditions = []
    params = []
    
    # PROBLEM 1 FIX: Using Wildcards "LIKE %...%" instead of Exact Equals "="
    if campus:
        conditions.append("LOWER(campus) LIKE @campus_val")
        params.append(bigquery.ScalarQueryParameter("campus_val", "STRING", f"%{campus.lower().strip()}%"))
    if department:
        conditions.append("LOWER(department) LIKE @dept_val")
        params.append(bigquery.ScalarQueryParameter("dept_val", "STRING", f"%{department.lower().strip()}%"))
        
    if not conditions:
        return "Error: You must provide at least one filter (campus or department)."
        
    where_clause = " AND ".join(conditions)
    sql = f"SELECT name, department, campus, image FROM `{PROJECT_ID}.{DATASET}.{TABLE}` WHERE {where_clause}"
    print(f"[DEBUG] SQL Executing: {sql}")
    
    try:
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = client.query(sql, job_config=job_config).to_dataframe()
        print(f"[DEBUG] Success! Found {len(df)} matching professors.")
        return df.to_string(index=False) if not df.empty else "No matching professors found for those specific filters."
    except Exception as e:
        print(f"[ERROR] EXCEPTION in Exact Filter:")
        traceback.print_exc()
        return f"Database error: {e}"

def mentor_detailed_info(professor_name: str) -> str:
    """Retrieves the full profile of a specific professor by name. Uses Tolerant Retrieval (Fuzzy Matching) to return up to 3 close matches."""
    print(f"\n[DEBUG] === TOOL: mentor_detailed_info ===")
    try:
        # Fetch all names to perform tolerant retrieval
        sql_names = f"SELECT name FROM `{PROJECT_ID}.{DATASET}.{TABLE}`"
        df_names = client.query(sql_names).to_dataframe()
        all_names = df_names['name'].tolist()
        
        # INCREASE TOLERANCE: Grab top 3 matches instead of just 1
        matches = difflib.get_close_matches(professor_name, all_names, n=3, cutoff=0.4)
        if not matches:
            return f"Professor '{professor_name}' is not found. No close matches exist in the database."
        
        print(f"[DEBUG] Tolerant Matches Found: {matches}")
        
        # Prepare the IN clause dynamically for BigQuery to fetch all matched profiles
        params = []
        in_clauses = []
        for i, match in enumerate(matches):
            param_name = f"match_{i}"
            in_clauses.append(f"@{param_name}")
            params.append(bigquery.ScalarQueryParameter(param_name, "STRING", match))
            
        in_clause_str = ", ".join(in_clauses)
        sql = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{TABLE}` WHERE name IN ({in_clause_str})"
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        df = client.query(sql, job_config=job_config).to_dataframe()
        
        header = f"Tolerant Search Result! You asked for '{professor_name}'. I found {len(matches)} close possibilities:\n\n"
        return header + df.to_string(index=False)
        
    except Exception as e:
        print(f"[ERROR] EXCEPTION:")
        traceback.print_exc()
        return f"Error connecting to database: {e}"



def mentor_semantic_recommendation(project_description: str) -> str:
    """Semantic search based on project topics using Vector Embeddings & Cosine Similarity."""
    print(f"\n[DEBUG] === TOOL: mentor_semantic_recommendation ===")
    try:
        # THE FIX: 
        # 1. Base table uses 'embedding'
        # 2. ML model outputs 'text_embedding', so we ALIAS it to 'embedding' to match!
        sql = f"""
            SELECT base.name, base.department, base.research, base.image
            FROM VECTOR_SEARCH(
                TABLE `{PROJECT_ID}.{DATASET}.{TABLE}`,
                'embedding', 
                (SELECT text_embedding AS embedding FROM ML.GENERATE_TEXT_EMBEDDING(
                    MODEL `{PROJECT_ID}.{DATASET}.{EMBEDDING_MODEL}`,
                    (SELECT @val AS content)
                )),
                top_k => 10,
                distance_type => 'COSINE'
            )
        """

        job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("val", "STRING", project_description)])
        df = client.query(sql, job_config=job_config).to_dataframe()
        
        if df.empty:
            return "No specific semantic match found for this topic."
        return df.to_string(index=False)
        
    except Exception as e:
        print(f"[ERROR] EXCEPTION:")
        traceback.print_exc()
        return f"Vector Search Database error: {str(e)}"
