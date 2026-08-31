'use client';

import React from 'react';
import './Spinner.css';

export default function Spinner({ size = 'medium', label = '' }) {
  return (
    <div className={`spinner-container spinner-${size}`}>
      <div className="spinner-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      {label && <p className="spinner-label">{label}</p>}
    </div>
  );
}
