import { useTranslations } from "next-intl";
import { Link } from "../../../i18n/navigation";

export default function Login() {
  const t = useTranslations("Login");

  return (
    <main>
      <h1>{t("title")}</h1>
      <p>{t("subtitle")}</p>

      <form>
        <input
          type="email"
          name="email"
          placeholder={t("emailPlaceholder")}
          autoComplete="email"
        />

        <input
          type="password"
          name="password"
          placeholder={t("passwordPlaceholder")}
          autoComplete="current-password"
        />

        <button type="submit">{t("submit")}</button>
      </form>

      <Link href="/signup">{t("register")}</Link>

      <br />

      <Link href="/forgot-password">
        {t("forgotPassword")}
      </Link>
    </main>
  );
}