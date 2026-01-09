# Student Marks and Report Generator

name = "Adith"
age = 22
marks = [78.5, 82.0, 91.5]

student = {
    "name": name,
    "age": age,
    "marks": marks
}

print(type(student["name"]))
print(type(student["age"]))
print(type(student["marks"]))

total = sum(marks)
average = total / len(marks)

print("Total Marks:", total)
print("Average:", average)

if average >= 50:
    print("Result: Pass")
else:
    print("Result: Fail")

