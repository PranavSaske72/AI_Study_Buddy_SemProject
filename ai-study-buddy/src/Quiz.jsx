import { useState } from "react";

function Quiz({ subject = "Python" }) {
  const questions = [
    {
      question: "What is Python?",
      options: [
        "A programming language",
        "A database",
        "An operating system",
        "A web browser",
      ],
      answer: "A programming language",
    },
    {
      question: "Which keyword is used to define a function in Python?",
      options: ["function", "def", "fun", "define"],
      answer: "def",
    },
    {
      question: "Which data type stores True or False?",
      options: ["String", "Integer", "Boolean", "List"],
      answer: "Boolean",
    },
    {
      question: "Which symbol is used for comments in Python?",
      options: ["//", "#", "/*", "<!--"],
      answer: "#",
    },
    {
      question: "Which function is used to display output in Python?",
      options: ["display()", "show()", "print()", "output()"],
      answer: "print()",
    },
  ];

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  const handleAnswer = (option) => {
    if (selectedAnswer) return;

    setSelectedAnswer(option);

    if (option === questions[currentQuestion].answer) {
      setScore((prevScore) => prevScore + 1);
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
      setSelectedAnswer("");
    } else {
      setFinished(true);
    }
  };

  const restartQuiz = () => {
    setCurrentQuestion(0);
    setSelectedAnswer("");
    setScore(0);
    setFinished(false);
  };

  if (finished) {
    return (
      <div className="quiz">
        <h2>🎉 Quiz Completed!</h2>

        <p>
          Your score: <strong>{score}</strong> / {questions.length}
        </p>

        <button onClick={restartQuiz}>
          🔄 Try Again
        </button>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="quiz">
      <h2>🧠 {subject} Quiz</h2>

      <p>
        Question {currentQuestion + 1} of {questions.length}
      </p>

      <h3>{question.question}</h3>

      <div className="quiz-options">
        {question.options.map((option) => (
          <button
            key={option}
            onClick={() => handleAnswer(option)}
            className={
              selectedAnswer === option ? "selected-option" : ""
            }
          >
            {option}
          </button>
        ))}
      </div>

      {selectedAnswer && (
        <button className="next-button" onClick={nextQuestion}>
          {currentQuestion === questions.length - 1
            ? "Finish Quiz"
            : "Next Question →"}
        </button>
      )}
    </div>
  );
}

export default Quiz;