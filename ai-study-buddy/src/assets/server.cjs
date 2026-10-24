const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const OpenAI = require("openai");

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.post("/api/ask", async (req, res) => {
  try {
    const { question, subject } = req.body;

    if (!question || !question.trim()) {
      return res.status(400).json({
        error: "Please enter a question.",
      });
    }

    const response = await client.responses.create({
      model: "gpt-5-mini",
      input: `You are an AI Study Buddy.

Subject: ${subject || "General"}

Student's question: ${question}

Explain the answer in simple language suitable for a college student.
Use short paragraphs and examples when helpful.`,
    });

    res.json({
      answer: response.output_text,
    });
  } catch (error) {
    console.error("AI Error:", error);

    res.status(500).json({
      error: "Something went wrong while getting the AI response.",
    });
  }
});

app.listen(5000, () => {
  console.log("🤖 AI server running at http://localhost:5000");
});