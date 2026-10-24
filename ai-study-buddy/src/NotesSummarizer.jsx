import { useState } from "react";

function NotesSummarizer() {
  const [subject, setSubject] = useState("");
  const [notes, setNotes] = useState("");
  const [summary, setSummary] = useState("");

  const summarizeNotes = () => {
    if (!subject.trim() || !notes.trim()) {
      setSummary("Please enter subject and notes first 😊");
      return;
    }

    const sentences = notes
      .split(/[.!?]+/)
      .map((sentence) => sentence.trim())
      .filter((sentence) => sentence.length > 0);

    const importantPoints = sentences.slice(0, 5);

    setSummary(
      importantPoints.length
        ? importantPoints
            .map((point, index) => `${index + 1}. ${point}`)
            .join("\n\n")
        : "Your notes are too short to summarize."
    );
  };

  return (
    <div className="planner">
      <h2>📝 AI Notes Summarizer</h2>
      <p>Enter your subject and notes to get important points.</p>

      <input
        type="text"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        placeholder="Enter subject (e.g. Artificial Intelligence)"
      />

      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Paste your notes here..."
        rows="8"
      />

      <button onClick={summarizeNotes}>
        ✨ Summarize Notes
      </button>

      {summary && (
        <div className="plan-result">
          <h3>📌 Important Points</h3>
          <pre>{summary}</pre>
        </div>
      )}
    </div>
  );
}

export default NotesSummarizer;