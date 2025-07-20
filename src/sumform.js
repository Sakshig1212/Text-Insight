
import React, { useState } from 'react';
import './Sumform.css';

const SummarizerForm = ({ handleSummarize }) => {
    const [inputText, setInputText] = useState('');
    const [selectedLength, setSelectedLength] = useState('medium'); // Default value
    const [selectedTone, setSelectedTone] = useState('neutral'); // Default value
    const [selectedFocus, setSelectedFocus] = useState('general'); // Default value

    // Handle form submission (pass values to parent)
    const handleSubmit = () => {
        handleSummarize(inputText, selectedLength, selectedTone, selectedFocus);
    };

    return (
        <div className="form-container">
            {/* Input Text Field */}
            <textarea
                className="input-text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter text here to get summarized text"
            />

            {/* Length Dropdown */}
            <select className="input-select" value={selectedLength} onChange={(e) => setSelectedLength(e.target.value)}>
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long</option>
            </select>

            {/* Tone Dropdown */}
            <select className="input-select" value={selectedTone} onChange={(e) => setSelectedTone(e.target.value)}>
    <option value="neutral">Neutral</option>
    <option value="formal">Formal</option>
    <option value="informal">Casual</option> {/* FIXED: value="informal" */}
</select>


            {/* Focus Dropdown */}
            <select className="input-select" value={selectedFocus} onChange={(e) => setSelectedFocus(e.target.value)}>
                <option value="general">General</option>
                <option value="technical">Technical</option>
                <option value="creative">Creative</option>
            </select>

            {/* Submit Button */}
            <button className="submit-button" onClick={handleSubmit}>
                Submit
            </button>
        </div>
    );
};

export default SummarizerForm;
