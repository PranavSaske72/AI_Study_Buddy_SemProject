import { useState } from "react";

function Studyplanner() {
  const [subject, setSubject] = useState("");
  const [hours, setHours] = useState("");
  const [plan, setPlan] = useState([]);

  const createPlan = () => {
    if (!subject.trim() || !hours) {
      setPlan(["Please enter subject and study hours 😊"]);
      return;
    }

    const totalHours = Number(hours);

    if (totalHours <= 0) {
      setPlan(["Please enter valid study hours."]);
      return;
    }

    const studyPlan = [
      `📚 Study ${subject} for ${totalHours} hour(s)`,
      "🧠 First 25 minutes: Learn the concept",
      "✍️ Next 20 minutes: Practice questions",
      "☕ Take a 5-minute break",
      "📝 Next 20 minutes: Revise important points",
      "🎯 Last 10 minutes: Test yourself",
    ];

    setPlan(studyPlan);
  };

  return (
    <div className="planner">
      <h2>📅 Study Planner</h2>

      <p>Create a simple study plan for your subject.</p>

      <input
        type="text"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        placeholder="Enter subject (e.g. Python)"
      />

      <input
        type="number"
        value={hours}
        onChange={(e) => setHours(e.target.value)}
        placeholder="Study hours"
        min="1"
      />

      <button onClick={createPlan}>
        ✨ Create Study Plan
      </button>

      {plan.length > 0 && (
        <div className="plan-result">
          <h3>📌 Your Study Plan</h3>

          {plan.map((item, index) => (
            <p key={index}>{item}</p>
          ))}
        </div>
      )}
    </div>
  );
}

export default Studyplanner;