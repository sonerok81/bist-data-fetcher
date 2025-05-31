# main.py
from pipeline import run_pipeline

if __name__ == "__main__":
    df = run_pipeline()
    print(df.to_string(index=False))
