
import { use } from "react";
import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { Link } from "../../../i18n/navigation";

export default function ForgotPassword({
  params,
}: PageProps<"/[locale]/forgot-password">) {
  const { locale } = use(params);
  setRequestLocale(locale);
  const t = useTranslations("ForgotPassword");

  return (
    <main>
      <h1>{t("title")}</h1>
      <p>{t("subtitle")}</p>

      <form>
        <input
          type="email"
          name="email"
          placeholder={t("emailPlaceholder")}
        />

        <button type="submit">{t("submit")}</button>
      </form>

      <Link href="/login">{t("backToLogin")}</Link>
    </main>
  );
}
