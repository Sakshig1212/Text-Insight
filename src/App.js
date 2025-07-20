

// export default App;
import React, { useState } from 'react';
import './App.css'; // Import the styles
import SummarizerForm from './sumform.js'; 

function App() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [loadingSummarize, setLoadingSummarize] = useState(false);
  const [loadingKeywords, setLoadingKeywords] = useState(false);

  // Handle the summarize function
  const handleSummarize = async (inputText, selectedLength, selectedTone, selectedFocus) => {
    setLoadingSummarize(true); // Start loading only for Summarize
    setLoadingKeywords(false);
    const response = await fetch("http://localhost:8000/summarize/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: inputText,
        length: selectedLength, // short, medium, long
        tone: selectedTone,     // neutral, formal, informal
        focus: selectedFocus    // general, technical, creative
      }),
    });

    if (response.ok) {
      const result = await response.json();
      setSummary(result.summary);
    } else {
      console.error("Error summarizing the text");
    }
    setLoadingSummarize(false);
  };

  // Handle the extract keywords function
  const handleExtractKeywords = async () => {
    setLoadingSummarize(false); // Stop summarize loading
    setLoadingKeywords(true);   // Start loading only for Keywords
    const response = await fetch("http://localhost:8000/extract_keywords/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    });

    if (response.ok) {
      const result = await response.json();
      setKeywords(result.keywords);
    } else {
      console.error("Error extracting keywords");
    }
    setLoadingKeywords(false);
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>TextInsight</h1>
        <p>Enter text below to get a summary and extract keywords!</p>
      </header>

      <div className="content">
        <SummarizerForm
          handleSummarize={handleSummarize}
        />

        <div className="button-container">
          <button
            className="btn"
            onClick={() => handleSummarize(text)}
            disabled={loadingSummarize}
          >
            {loadingSummarize ? "Summarizing..." : "Summarize"}
          </button>

          <button
            className="btn"
            onClick={handleExtractKeywords}
            disabled={loadingKeywords}
          >
            {loadingKeywords ? "Extracting..." : "Extract Keywords"}
          </button>
        </div>

        {summary && (
          <div className="output-container">
            <h2>Summary:</h2>
            <p className="output-text">{summary}</p>
          </div>
        )}

        {keywords.length > 0 && (
          <div className="keywords-container">
            <h2>Extracted Keywords:</h2>
            <ul className="keywords-list">
              {keywords.map((keyword, index) => (
  <li key={index} className="keyword-item">
    {keyword}
  </li>
))}

            </ul>
          </div>
        )}
      </div>

      <footer className="footer">
        <p>Thanks for visiting!</p>
      </footer>
    </div>
  );
}

export default App;
