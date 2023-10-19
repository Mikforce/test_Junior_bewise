from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import psycopg2
from datetime import datetime
import uvicorn

app = FastAPI()

class Question(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

@app.post("/questions/")
def get_questions(questions_num: int):
    conn = psycopg2.connect("dbname=your_database user=your_username password=your_password host=localhost port=5432")
    cur = conn.cursor()

    cur.execute("SELECT question FROM questions")
    existing_questions = cur.fetchall()
    existing_questions = [question[0] for question in existing_questions]

    new_questions = []
    while len(new_questions) < questions_num:
        response = requests.get(f"https://jservice.io/api/random?count={questions_num}")
        if response.status_code == 200:
            response_data = response.json()
            for question_data in response_data:
                question = Question(
                    id=question_data["id"],
                    question=question_data["question"],
                    answer=question_data["answer"],
                    created_at=datetime.now()
                )
                if question.question not in existing_questions:
                    new_questions.append(question)
                    existing_questions.append(question.question)

    cur.executemany(
        "INSERT INTO questions (id, question, answer, created_at) VALUES (%s, %s, %s, %s)",
        [(q.id, q.question, q.answer, q.created_at) for q in new_questions]
    )

    conn.commit()
    cur.close()
    conn.close()

    if len(new_questions) > 0:
        return new_questions[0]
    else:
        raise HTTPException(status_code=404, detail="No questions available")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)