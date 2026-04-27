{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "35f5e755",
   "metadata": {},
   "outputs": [],
   "source": [
    "import sqlite3\n",
    "\n",
    "def setup_db():\n",
    "    conn = sqlite3.connect('sdu_university.db')\n",
    "    cursor = conn.cursor()\n",
    "\n",
    "    # Таблица курсов\n",
    "    cursor.execute('''CREATE TABLE IF NOT EXISTS Courses \n",
    "                      (id INTEGER PRIMARY KEY, title TEXT, credits INTEGER, department TEXT)''')\n",
    "    \n",
    "    # Таблица преподавателей и расписания\n",
    "    cursor.execute('''CREATE TABLE IF NOT EXISTS Schedule \n",
    "                      (id INTEGER PRIMARY KEY, course_id INTEGER, instructor TEXT, day TEXT, room TEXT,\n",
    "                       FOREIGN KEY(course_id) REFERENCES Courses(id))''')\n",
    "    \n",
    "    # Таблица отзывов/сложности (для \"Vibe-coding\" анализа)\n",
    "    cursor.execute('''CREATE TABLE IF NOT EXISTS VibeCheck \n",
    "                      (id INTEGER PRIMARY KEY, course_id INTEGER, difficulty TEXT, feedback TEXT,\n",
    "                       FOREIGN KEY(course_id) REFERENCES Courses(id))''')\n",
    "\n",
    "    # Наполнение тестовыми данными\n",
    "    courses = [\n",
    "        (1, 'Introduction to AI', 5, 'Engineering'),\n",
    "        (2, 'Database Management', 5, 'Engineering'),\n",
    "        (3, 'Business Ethics', 3, 'Business School')\n",
    "    ]\n",
    "    cursor.executemany('INSERT OR IGNORE INTO Courses VALUES (?,?,?,?)', courses)\n",
    "    \n",
    "    schedule = [(1, 1, 'Mr. Maratov', 'Monday', 'Room 302'), (2, 2, 'Ms. Dana', 'Wednesday', 'Room 105')]\n",
    "    cursor.executemany('INSERT OR IGNORE INTO Schedule VALUES (?,?,?,?,?)', schedule)\n",
    "    \n",
    "    vibes = [(1, 1, 'Hard', 'Very interesting, but lots of math'), (2, 2, 'Medium', 'Practical and useful')]\n",
    "    cursor.executemany('INSERT OR IGNORE INTO VibeCheck VALUES (?,?,?,?)', vibes)\n",
    "\n",
    "    conn.commit()\n",
    "    conn.close()\n",
    "    print(\"Database SDU created successfully!\")\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    setup_db()"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
