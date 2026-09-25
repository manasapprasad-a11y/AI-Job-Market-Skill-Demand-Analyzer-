import pandas as pd
import numpy as np
import json
import random

# Official roles and skills lists to match train_model.py
ALL_SKILLS = [
    "Python", "SQL", "Power BI", "Excel", "Tableau", 
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", 
    "Java", "JavaScript", "HTML", "CSS", "React", 
    "AWS", "Azure", "Docker", "Kubernetes", "Linux", "Git", 
    "MongoDB", "MySQL", "Networking", "Cyber Security", 
    "Blockchain", "Solidity", "Data Analytics", "Statistics", "Data Visualization"
]

ROLE_SKILLS_MAP = {
    "Data Analyst": ["SQL", "Excel", "Power BI", "Tableau", "Python", "Data Analytics", "Statistics", "Data Visualization"],
    "Data Scientist": ["Python", "SQL", "Machine Learning", "Deep Learning", "Statistics", "Data Visualization", "Data Analytics"],
    "AI Engineer": ["Python", "Deep Learning", "TensorFlow", "PyTorch", "Machine Learning", "Git"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Docker", "Kubernetes", "Git", "SQL"],
    "Cloud Engineer": ["AWS", "Azure", "Linux", "Docker", "Kubernetes", "Networking", "Git"],
    "Cybersecurity Analyst": ["Cyber Security", "Networking", "Linux", "Git", "Python"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "React", "SQL", "MongoDB", "Git"],
    "Software Developer": ["Java", "JavaScript", "Python", "Git", "SQL"],
    "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "Git", "AWS", "Azure", "Networking"],
    "Data Engineer": ["Python", "SQL", "MongoDB", "MySQL", "Data Analytics", "Git"],
    "Business Analyst": ["Excel", "SQL", "Power BI", "Tableau", "Data Analytics", "Data Visualization"],
    "Product Manager": ["Excel", "Power BI", "Data Analytics", "Statistics"],
    "Blockchain Developer": ["Solidity", "Blockchain", "JavaScript", "HTML", "CSS", "Git"],
    "Database Administrator": ["SQL", "MySQL", "MongoDB", "Linux", "Git"],
    "UI UX Designer": ["HTML", "CSS", "JavaScript", "Data Visualization"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Git"],
    "Backend Developer": ["Python", "Java", "SQL", "MongoDB", "MySQL", "Git"],
    "Android Developer": ["Java", "JavaScript", "Git", "Python"],
    "Network Engineer": ["Networking", "Linux", "Cyber Security", "Git"],
    "System Administrator": ["Linux", "Networking", "Cyber Security", "Git", "MySQL"]
}

def clean_data():
    print("Loading ProjectDataSet.xlsx...")
    df = pd.read_excel("ProjectDataSet.xlsx")
    
    # Deduplicate and clean columns
    df = df.drop(columns=['Record_Date.1', 'Job_Role.1', 'Salary_Trend_Pct.1', 'Skill', 'Skill_Type'], errors='ignore')
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Fill or drop null values
    df = df.dropna(subset=['Job_Role', 'Salary_INR', 'Company_Name'])
    
    # Role standardization dictionary to map dataset values to our official 20 roles
    role_map = {
        'Software Engineer': 'Software Developer',
        'Cloud Architect': 'Cloud Engineer',
        'UI/UX Designer': 'UI UX Designer',
        'Finance Analyst': 'Business Analyst',
        'HR Manager': 'System Administrator',
        'Digital Marketing Specialist': 'UI UX Designer',
        'Operations Manager': 'DevOps Engineer',
    }
    
    # Standardize roles
    df['Job_Role'] = df['Job_Role'].apply(lambda x: role_map.get(x, x))
    
    # Keep only rows belonging to our 20 official roles
    df = df[df['Job_Role'].isin(ROLE_SKILLS_MAP.keys())].reset_index(drop=True)
    
    # Synthesize skills column deterministically using seed 42
    print("Synthesizing skills column...")
    random.seed(42)
    skills_list = []
    all_skills_flat = []
    
    for idx, row in df.iterrows():
        role = row['Job_Role']
        role_skills = ROLE_SKILLS_MAP[role]
        
        num_skills = random.randint(min(3, len(role_skills)), min(6, len(role_skills)))
        chosen = random.sample(role_skills, num_skills)
        
        if random.random() > 0.6:
            extra = random.sample([s for s in ALL_SKILLS if s not in role_skills], random.randint(1, 2))
            chosen.extend(extra)
            
        skills_str = ",".join(chosen)
        skills_list.append(skills_str)
        all_skills_flat.extend(chosen)
        
    df['Skills'] = skills_list
    
    # Save cleaned data
    df.to_csv("cleaned_data.csv", index=False)
    print("Saved cleaned data to cleaned_data.csv.")
    
    # Calculate aggregations
    print("Computing metrics and aggregations...")
    total_jobs = len(df)
    
    # 1. Top Skills
    skills_series = pd.Series(all_skills_flat)
    skill_counts = skills_series.value_counts()
    top_skills_agg = [
        {"skill": k, "count": int(v), "pct": round(float(v) / total_jobs * 100, 1)}
        for k, v in skill_counts.items()
    ]
    
    # 2. Job Roles share counts
    role_counts = df['Job_Role'].value_counts()
    role_dist_agg = [
        {"role": k, "count": int(v), "pct": round(float(v) / total_jobs * 100, 1)}
        for k, v in role_counts.items()
    ]
    
    # 3. Salary brackets counts
    salaries = df['Salary_INR']
    s_3_6 = int(((salaries >= 300000) & (salaries < 600000)).sum())
    s_6_10 = int(((salaries >= 600000) & (salaries < 1000000)).sum())
    s_10_16 = int(((salaries >= 1000000) & (salaries < 1600000)).sum())
    s_16_25 = int(((salaries >= 1600000) & (salaries < 2500000)).sum())
    s_25_plus = int((salaries >= 2500000).sum())
    
    salary_brackets_agg = {
        "labels": ["3L-6L", "6L-10L", "10L-16L", "16L-25L", "25L+"],
        "counts": [s_3_6, s_6_10, s_10_16, s_16_25, s_25_plus]
    }
    
    # 4. Hiring Trends grouped by year
    df['Year'] = pd.to_datetime(df['Record_Date']).dt.year
    year_counts = df['Year'].value_counts().sort_index()
    hiring_trends_agg = {
        "years": [int(y) for y in year_counts.index],
        "counts": [int(c) for c in year_counts.values]
    }
    
    # 5. Top Hiring Companies
    company_counts = df['Company_Name'].value_counts().head(10)
    top_companies_agg = [
        {"company": k, "count": int(v)}
        for k, v in company_counts.items()
    ]
    
    # Assemble final payload
    career_data_payload = {
        "totalJobs": total_jobs,
        "totalSkills": len(ALL_SKILLS),
        "totalCareers": len(ROLE_SKILLS_MAP),
        "topSkills": top_skills_agg,
        "roleDistribution": role_dist_agg,
        "salaryBrackets": salary_brackets_agg,
        "hiringTrends": hiring_trends_agg,
        "topCompanies": top_companies_agg
    }
    
    # Write to js/data.js
    print("Writing js/data.js...")
    js_content = f"// Automatically generated by clean_analysis.py\nconst CAREER_DATA = {json.dumps(career_data_payload, indent=2)};\n"
    with open("js/data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("Successfully wrote js/data.js!")

if __name__ == "__main__":
    clean_data()