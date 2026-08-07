import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as app_module

print("Testing Assessment Logic for English, age=8, Basic level:")

questions = app_module.get_assessment_questions("English", age=8, learning_level="Basic")
for idx, q in enumerate(questions):
    print(f"\nQuestion {idx + 1}:")
    print(f"  Name: {q.get('name')}")
    print(f"  Type: {q.get('type')}")
    print(f"  Skill: {q.get('skill')}")
    print(f"  Prompt: {q.get('prompt')}")
    if q.get('image'):
        print(f"  Image: {q.get('image')}")
    if q.get('text'):
        print(f"  Text: {q.get('text')}")
    print(f"  Options: {q.get('options')}")
    print(f"  Answer: {q.get('answer')}")
