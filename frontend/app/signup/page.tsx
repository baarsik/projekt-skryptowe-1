import Link from "next/link";

export default function Signup() {
  return (
    <main>
      <h1>Sign up</h1>

      <form>
        <input type="text" placeholder="Name" />
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button type="submit">Create account</button>
      </form>

      <Link href="/login">Already have an account? Login</Link>
    </main>
  );
}