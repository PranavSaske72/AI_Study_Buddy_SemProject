import { useState } from "react";
import "./App.css";
import Quiz from "./Quiz";
import StudyPlanner from "./StudyPlanner";
import NotesSummarizer from "./NotesSummarizer";

function App() {
  const [selectedSubject, setSelectedSubject] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [showQuiz, setShowQuiz] = useState(false);
  const [showPlanner, setShowPlanner] = useState(false);
  const [showNotes, setShowNotes] = useState(false);

  const subjects = [
    "Python",
    "DBMS",
    "Web Development",
    "Artificial Intelligence",
    "Mathematics",
    "Data Science",
  ];

  const askAI = () => {
    if (!question.trim()) {
      setAnswer("Please type a question first 😊");
      return;
    }

    setAnswer(
      `🤖 AI Study Buddy:\n\nHere's a simple explanation of your question about ${selectedSubject}:\n\n"${question}"\n\nI'm ready to help you understand this topic step-by-step! 📚`
    );
  };

  const selectSubject = (subject) => {
    setSelectedSubject(subject);
    setQuestion("");
    setAnswer("");
    setShowQuiz(false);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>🤖 AI Study Buddy</h1>
          <p>Your smart companion for learning</p>
        </div>

        <button className="profile">👤</button>
      </header>

      <main className="container">

        <section className="welcome">
          <h2>Welcome back, Student! 👋</h2>
          <p>What would you like to study today?</p>
        </section>

        <section className="subjects">
          <h2>📚 Choose a Subject</h2>

          <div className="subject-grid">
            {subjects.map((subject) => (
              <button
                key={subject}
                className="subject-card"
                onClick={() => selectSubject(subject)}
              >
                <span>📖</span>
                <strong>{subject}</strong>
              </button>
            ))}
          </div>
        </section>

        {selectedSubject && (
          <section className="selected">
            <h2>✨ {selectedSubject}</h2>

            <p>Ask anything about {selectedSubject}.</p>

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={`Ask a question about ${selectedSubject}...`}
            />

            <button className="ask-button" onClick={askAI}>
              🤖 Ask AI
            </button>

            {answer && (
              <div className="answer">
                {answer}
              </div>
            )}

            <button
              className="ask-button"
              onClick={() => setShowQuiz(true)}
            >
              🧠 Start Smart Quiz
            </button>

            {showQuiz && (
              <>
                <Quiz subject={selectedSubject} />

                <button
                  className="ask-button"
                  onClick={() => setShowQuiz(false)}
                >
                  ✖ Close Quiz
                </button>
              </>
            )}
          </section>
        )}

        <section className="features">

          <div
            className="feature-card"
            onClick={() => setShowNotes(!showNotes)}
            style={{ cursor: "pointer" }}
          >
            <span>📝</span>
            <h3>Notes Summarizer</h3>
            <p>Paste your notes and get important points.</p>
          </div>

          <div
            className="feature-card"
            onClick={() => {
              if (selectedSubject) {
                setShowQuiz(true);
              } else {
                setAnswer("Please choose a subject first 😊");
              }
            }}
            style={{ cursor: "pointer" }}
          >
            <span>🧠</span>
            <h3>Smart Quiz</h3>
            <p>Practice your knowledge with quizzes.</p>
          </div>

          <div
            className="feature-card"
            onClick={() => setShowPlanner(!showPlanner)}
            style={{ cursor: "pointer" }}
          >
            <span>📅</span>
            <h3>Study Planner</h3>
            <p>Create a personalized study schedule.</p>
          </div>

        </section>

        {showNotes && (
          <>
            <NotesSummarizer />

            <button
              className="ask-button"
              onClick={() => setShowNotes(false)}
            >
              ✖ Close Notes
            </button>
          </>
        )}

        {showPlanner && (
          <>
            <StudyPlanner />

            <button
              className="ask-button"
              onClick={() => setShowPlanner(false)}
            >
              ✖ Close Planner
            </button>
          </>
        )}

      </main>
    </div>
  );
}

export default App;