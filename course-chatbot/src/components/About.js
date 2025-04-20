import React from 'react';

const About = ({ onClose }) => {
  return (
    <div className="about-container">
      <div className="about-content">
        <h1>About Northwestern CTECs Assistant</h1>
        
        <section>
          <h2>What is this tool?</h2>
          <p>The Northwestern CTECs Assistant helps students navigate course information and professor reviews from Northwestern's Course and Teacher Evaluation Council (CTECs) database.</p>
        </section>
        
        <section>
          <h2>How to use</h2>
          <p>Simply ask questions about Northwestern courses, professors, or departments. For example:</p>
          <ul>
            <li>"What are the best Computer Science courses?"</li>
            <li>"Tell me about Professor Smith in the Economics department"</li>
            <li>"What classes in the Economics department have the least time commitment?"</li>
          </ul>
          <p><strong>Note: Every request is processed independent of prior requests, even if they are in the same chat.</strong></p>
        </section>
        
        <section>
          <h2>Data Sources</h2>
          <p>This tool uses data from Northwestern University's official CTECs database, updated quarterly.</p>
          <p><strong>Currently, the tool only has data from CS classes up to CS 394.</strong></p>
        </section>
        
        <section>
          <h2>Privacy</h2>
          <p>We respect your privacy. Your conversations are stored only to improve the quality of responses and are not shared with third parties.</p>
        </section>
        
        <button className="logout-button" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default About; 