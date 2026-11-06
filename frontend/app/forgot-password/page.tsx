import Link from "next/link";

export default function ForgotPassword() {
  return (
    <main>
      <h1>Forgot password?</h1>

      <form>
        <input type="email" placeholder="Enter your email" />
        <button type="submit">Reset password</button>
      </form>

      <Link href="/login">Back to login</Link>
    </main>
  );
}