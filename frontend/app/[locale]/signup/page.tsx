
import { useTranslations } from "next-intl";
import { Link } from "../../../i18n/navigation";

export default function Signup() {
  const t = useTranslations("Register");

  return (
    <main>
      <h1>{t("title")}</h1>
      <p>{t("subtitle")}</p>

      <form>
        <input
          type="text"
          name="name"
          placeholder={t("name")}
        />

        <input
          type="email"
          name="email"
          placeholder={t("emailPlaceholder")}
        />

        <input
          type="password"
          name="password"
          placeholder={t("passwordPlaceholder")}
        />

        <input
          type="password"
          name="confirmPassword"
          placeholder={t("confirmPasswordPlaceholder")}
        />

        <button type="submit">{t("submit")}</button>
      </form>

      <p>
        {t("hasAccount")}{" "}
        <Link href="/login">{t("login")}</Link>
      </p>
    </main>
  );
}
