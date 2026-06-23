const { useState } = React;

function AuthScreen({ onAuth }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const fn = mode === "login" ? login : signup;
      const data = await fn(email, password);
      onAuth(data);
    } catch (err) {
      setError(err.message || "Erro inesperado.");
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setMode(mode === "login" ? "signup" : "login");
    setError("");
  };

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <h1 className="auth-brand">ChatLLM Lab</h1>
        <h2 className="auth-title">{mode === "login" ? "Entrar" : "Criar Conta"}</h2>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Seu email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
          <input
            type="password"
            placeholder="Sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar Conta"}
          </button>
        </form>

        <p className="auth-toggle">
          {mode === "login" ? (
            <>Nao tem conta? <a href="#" onClick={(e) => { e.preventDefault(); toggleMode(); }}>Cadastre-se</a></>
          ) : (
            <>Ja tem conta? <a href="#" onClick={(e) => { e.preventDefault(); toggleMode(); }}>Entrar</a></>
          )}
        </p>
      </div>
    </main>
  );
}