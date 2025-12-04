// FILE: src/App.jsx
import React from "react";

function App() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>AgriScan Dashboard</h1>
        <p style={styles.subtitle}>
          Real-time monitoring and analytics for your fields
        </p>
        <p style={styles.cardText}>
          This dashboard allows you to manage your farm efficiently. Use the sidebar to navigate through live feeds, field analytics, and reports.
        </p>
        <button style={styles.button}>Get Started</button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    fontFamily: "Arial, sans-serif",
    display: "flex",
    justifyContent: "center", // horizontal center
    alignItems: "center",     // vertical center
    height: "100vh",          // full viewport height
    margin: 0,
    backgroundColor: "#f4f6f8",
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: "10px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    maxWidth: "800px",
    width: "90%",
    textAlign: "center",
    padding: "2rem",
  },
  title: {
    fontSize: "2.5rem",
    margin: "0 0 0.5rem 0",
  },
  subtitle: {
    fontSize: "1.2rem",
    margin: "0 0 1rem 0",
    color: "#555",
  },
  cardText: {
    fontSize: "1rem",
    marginBottom: "2rem",
    color: "#333",
  },
  button: {
    backgroundColor: "#0d6efd",
    color: "#fff",
    border: "none",
    padding: "0.75rem 1.5rem",
    borderRadius: "5px",
    cursor: "pointer",
    fontSize: "1rem",
  },
};

export default App;
