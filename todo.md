- Dynamic few-shot prompting
   - [X] Figure out how to open cypher example self-service portal
   - [X] Update README
   - [X] Ensure embeddings are never read in directly
   - Try adding the Cypher query to the QA prompt as additional context
    - [X] Test adding and removing examples
    - Add more unit tests
    - Add all examples to csv
    - Clean repo
    - Write article
- Create example question gallery on GitHub
- Incorrect examples
- Dev ops
    - Unit tests
        - Cypher queries run successfully
    - Pre-commit
    - Github workflows
- Memory (with redis)
- Email tool
- Dynamic foundation models (including open-source) (llama 3.1)
- Generating visualizations
- Streaming
- Query corrector
- Security (read-only access to Neo4j)
- Review sentiment classifier




- What is the average duration in days for closed emergency visits? [fixed with extra example with gpt-4o-mini]
- What was the total billing amount charged to each payer for 2023? [fixed with extra example with gpt-4o-mini]
- What is the average billing amount for medicaid visits? [fixed with original examples]
- What is the average billing amount per day for Aetna patients? [fixed with original examples]
- For visits that are not missing chief complaints, what percentage have reviews? [fixed with extra example with gpt-4o-mini]

- For visits in Georgia in 2023 that are not missing chief complaints, what percentage have reviews?
- List every review for visits treated by physician 270. Don't leave any out. [fixed with QA prompt change]
- How much was billed for patient 789's stay? [fixed with extra example with gpt-4o-mini]


Add these after you write the article:

[{'q': {'question': 'Which state had the largest percent increase in Cigna visits from 2022 to 2023?',
   'cypher': "\n    MATCH (h:Hospital)<-[:AT]-(v:Visit)-[:COVERED_BY]->(p:Payer)\n    WHERE lower(p.name) = 'cigna' AND v.admission_date >= '2022-01-01' AND\n    v.admission_date < '2024-01-01'\n    WITH h.state_name AS state, COUNT(v) AS visit_count,\n        SUM(CASE WHEN v.admission_date >= '2022-01-01' AND\n        v.admission_date < '2023-01-01' THEN 1 ELSE 0 END) AS count_2022,\n        SUM(CASE WHEN v.admission_date >= '2023-01-01' AND\n        v.admission_date < '2024-01-01' THEN 1 ELSE 0 END) AS count_2023\n    WITH state, visit_count, count_2022, count_2023,\n        (toFloat(count_2023) - toFloat(count_2022)) / toFloat(count_2022) * 100\n        AS percent_increase\n    RETURN state, percent_increase\n    ORDER BY percent_increase DESC\n    LIMIT 1\n    "}},
 {'q': {'question': 'what is the average duration in days for closed elective visits?',
   'cypher': "MATCH (v:Visit)\nWHERE lower(v.status) = 'discharged' AND lower(v.admission_type) = 'elective'\nRETURN AVG(duration.inDays(date(v.admission_date), date(v.discharge_date)).days) AS average_duration_days"}},
 {'q': {'question': 'what was the total billing amount charged by each hospital for 2023?',
   'cypher': "MATCH (p:Payer)<-[c:COVERED_BY]-(v:Visit)-[a:AT]-(h:Hospital)\nWHERE v.admission_date >= '2023-01-01' AND v.admission_date < '2024-01-01'\nRETURN h.name AS hospital_name, SUM(c.billing_amount) AS total_billing_amount"}},
 {'q': {'question': 'for visits that are missing chief complaints, what percentage have reviews?',
   'cypher': 'MATCH (v:Visit)\nWHERE v.chief_complaint IS NULL\nWITH COUNT(v) AS total_visits\nMATCH (v)-[:WRITES]->(r:Review)\nWITH total_visits, COUNT(r) AS visits_with_reviews\nRETURN (toFloat(visits_with_reviews) / total_visits) * 100 AS percentage_with_reviews'}},
 {'q': {'question': 'Who is the oldest patient and how old are they?',
   'cypher': '\n    MATCH (p:Patient)\n    RETURN p.name AS oldest_patient,\n        duration.between(date(p.dob), date()).years AS age\n    ORDER BY age DESC\n    LIMIT 1\n    '}},
 {'q': {'question': 'Which physician has billed the least to Cigna',
   'cypher': "\n    MATCH (p:Payer)<-[c:COVERED_BY]-(v:Visit)-[t:TREATS]-(phy:Physician)\n    WHERE lower(p.name) = 'cigna'\n    RETURN phy.name AS physician_name, SUM(c.billing_amount) AS total_billed\n    ORDER BY total_billed\n    LIMIT 1\n    "}},
 {'q': {'question': 'How many non-emergency patients in North Carolina have written reviews?',
   'cypher': "\n    match (r:Review)<-[:WRITES]-(v:Visit)-[:AT]->(h:Hospital)\n    where lower(h.state_name) = 'nc' and lower(v.admission_type) <> 'emergency'\n    return count(*)\n    "}},
 {'q': {'question': "how much was billed for patient 123's stay?",
   'cypher': 'MATCH (p:Patient {id: 123})-[:HAS]->(v:Visit)-[c:COVERED_BY]->(:Payer)\nRETURN SUM(c.billing_amount) AS total_billed'}}]
