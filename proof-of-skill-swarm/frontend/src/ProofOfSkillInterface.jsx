import React, { useState, useEffect } from 'react';
import './ProofOfSkillInterface.css';

const ProofOfSkillInterface = () => {
  const [intent, setIntent] = useState('');
  const [currentChallenge, setCurrentChallenge] = useState(null);
  const [solution, setSolution] = useState('');
  const [proof, setProof] = useState(null);
  const [skillNFT, setSkillNFT] = useState(null);
  const [processingState, setProcessingState] = useState('idle');
  const [error, setError] = useState(null);
  const [tasksCompleted, setTasksCompleted] = useState([]);

  const API_BASE = {
    intent: process.env.REACT_APP_QUANTUM_INTENT_URL || 'http://localhost:3001',
    challenge: process.env.REACT_APP_CHALLENGE_GENERATOR_URL || 'http://localhost:3002',
    proof: process.env.REACT_APP_ZK_PROOF_URL || 'http://localhost:3005',
    nft: process.env.REACT_APP_SKILL_NFT_URL || 'http://localhost:3007'
  };

  const processIntent = async () => {
    try {
      setProcessingState('capturing');
      setError(null);

      // Step 1: Quantum Intent Processing
      const intentResponse = await fetch(`${API_BASE.intent}/api/v1/intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent, context: {} })
      });

      if (!intentResponse.ok) throw new Error('Failed to process intent');
      const processedIntent = await intentResponse.json();

      setProcessingState('generating');

      // Step 2: Generate Challenge
      const challengeResponse = await fetch(`${API_BASE.challenge}/api/v1/challenge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          processedIntent: processedIntent.processedIntent,
          personalization: {}
        })
      });

      if (!challengeResponse.ok) throw new Error('Failed to generate challenge');
      const challenge = await challengeResponse.json();
      
      setCurrentChallenge({...challenge, startTime: Date.now()});
      setProcessingState('ready');
      setTasksCompleted([]);

    } catch (err) {
      setError(err.message);
      setProcessingState('idle');
    }
  };

  const submitSolution = async () => {
    try {
      setProcessingState('proving');
      setError(null);

      // Get wallet address (mock for demo)
      const solverAddress = '0x' + Math.random().toString(16).substr(2, 40);

      // Step 3: Generate ZK-Proof
      const proofResponse = await fetch(`${API_BASE.proof}/api/v1/proof`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challengeData: currentChallenge,
          solutionData: {
            solution,
            completionTime: Math.floor((Date.now() - currentChallenge.startTime) / 1000),
            tasksCompleted: tasksCompleted.length
          },
          solverAddress
        })
      });

      if (!proofResponse.ok) throw new Error('Failed to generate proof');
      const generatedProof = await proofResponse.json();

      setProof(generatedProof);
      setProcessingState('verifying');

      // Step 4: Verify Proof
      const verifyResponse = await fetch(
        `${API_BASE.proof}/api/v1/proof/${generatedProof.proofId}/verify`,
        { method: 'POST' }
      );

      if (!verifyResponse.ok) throw new Error('Failed to verify proof');
      const verificationResult = await verifyResponse.json();

      setProof({...generatedProof, ...verificationResult});
      setProcessingState('complete');

      // Mock NFT minting
      setSkillNFT({
        tokenId: Math.floor(Math.random() * 10000),
        skillType: currentChallenge.domain,
        proficiencyLevel: Math.floor(verificationResult.score / 10),
        verificationCount: 1
      });

    } catch (err) {
      setError(err.message);
      setProcessingState('ready');
    }
  };

  const toggleTask = (taskId) => {
    setTasksCompleted(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    );
  };

  const getProcessingStateText = () => {
    const states = {
      'idle': 'Ready',
      'capturing': 'Processing Intent...',
      'generating': 'Generating Challenge...',
      'ready': 'Ready to Submit',
      'proving': 'Generating Proof...',
      'verifying': 'Verifying Proof...',
      'complete': 'Complete!'
    };
    return states[processingState] || processingState;
  };

  return (
    <div className="proof-of-skill-interface">
      <header className="interface-header">
        <h1>🌟 Proof-of-Skill Swarm</h1>
        <p>Transform your skills into verifiable, valuable NFTs</p>
      </header>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="intent-section">
        <h2>What skill do you want to prove?</h2>
        <textarea
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="e.g., I want to prove my React debugging ability"
          className="intent-input"
          disabled={processingState !== 'idle'}
        />
        <button 
          onClick={processIntent} 
          disabled={processingState !== 'idle' || !intent.trim()}
          className="primary-button"
        >
          {processingState === 'idle' ? 'Generate Challenge' : getProcessingStateText()}
        </button>
      </div>

      {currentChallenge && (
        <div className="challenge-section">
          <h2>🎯 Challenge: {currentChallenge.title}</h2>
          
          <div className="challenge-metadata">
            <span className="badge">Domain: {currentChallenge.domain}</span>
            <span className="badge">Difficulty: {currentChallenge.difficulty}/10</span>
            <span className="badge">Time Limit: {currentChallenge.timeLimit} min</span>
            <span className="badge reward">Reward: {currentChallenge.reward} tokens</span>
          </div>

          <div className="challenge-description">
            <p>{currentChallenge.description}</p>
          </div>

          {currentChallenge.tasks && currentChallenge.tasks.length > 0 && (
            <div className="tasks-section">
              <h3>Tasks</h3>
              <ul className="task-list">
                {currentChallenge.tasks.map(task => (
                  <li key={task.id} className="task-item">
                    <label>
                      <input
                        type="checkbox"
                        checked={tasksCompleted.includes(task.id)}
                        onChange={() => toggleTask(task.id)}
                        disabled={processingState !== 'ready'}
                      />
                      <span className={task.required ? 'required' : ''}>
                        {task.description}
                        {task.required && ' *'}
                      </span>
                      <span className="task-points">{task.points} pts</span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="solution-section">
            <h3>Submit Your Solution</h3>
            <textarea
              value={solution}
              onChange={(e) => setSolution(e.target.value)}
              placeholder="Paste your solution here..."
              className="solution-input"
              disabled={processingState !== 'ready'}
            />
            <button 
              onClick={submitSolution} 
              disabled={processingState !== 'ready' || !solution.trim()}
              className="primary-button"
            >
              {processingState === 'ready' ? 'Submit Solution' : getProcessingStateText()}
            </button>
          </div>
        </div>
      )}

      {proof && (
        <div className="proof-section">
          <h2>✅ Proof Generated</h2>
          <div className="proof-card">
            <div className="proof-detail">
              <label>Proof ID:</label>
              <code>{proof.proofId}</code>
            </div>
            <div className="proof-detail">
              <label>Verification Status:</label>
              <span className={proof.verified ? 'verified' : 'pending'}>
                {proof.verified ? 'Verified ✓' : 'Pending...'}
              </span>
            </div>
            <div className="proof-detail">
              <label>Score:</label>
              <span className="score">{proof.score}/100</span>
            </div>
            <div className="proof-detail">
              <label>Proof Type:</label>
              <span>{proof.proofType}</span>
            </div>
            <div className="proof-detail">
              <label>Security:</label>
              <span>{proof.securityLevel}</span>
            </div>
          </div>
        </div>
      )}

      {skillNFT && (
        <div className="nft-section">
          <h2>🏆 Skill NFT Minted!</h2>
          <div className="nft-card">
            <div className="nft-image">
              <div className="nft-badge">
                <span className="level">{skillNFT.proficiencyLevel}</span>
                <span className="label">Level</span>
              </div>
            </div>
            <div className="nft-details">
              <div className="nft-detail">
                <label>Token ID:</label>
                <span>#{skillNFT.tokenId}</span>
              </div>
              <div className="nft-detail">
                <label>Skill Type:</label>
                <span>{skillNFT.skillType}</span>
              </div>
              <div className="nft-detail">
                <label>Proficiency Level:</label>
                <span>{skillNFT.proficiencyLevel}/10</span>
              </div>
              <div className="nft-detail">
                <label>Verification Count:</label>
                <span>{skillNFT.verificationCount}</span>
              </div>
            </div>
            <div className="nft-actions">
              <button className="secondary-button">View on Explorer</button>
              <button className="secondary-button">Share Proof</button>
              <button className="secondary-button">Create TBA</button>
            </div>
          </div>
        </div>
      )}

      <footer className="interface-footer">
        <p>Powered by Cognitive Genesis Protocol</p>
      </footer>
    </div>
  );
};

export default ProofOfSkillInterface;
