import Link from "next/link";

export default function Login() {
  return (
    <main>
      <h1>Login</h1>

      <form>
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button type="submit">Login</button>
      </form>

      <Link href="/signup">Sign up</Link>
      <br />
      <Link href="/forgot-password">Forgot password?</Link>
    </main>
  );
}