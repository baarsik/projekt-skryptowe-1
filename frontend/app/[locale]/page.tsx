
import { use } from "react";
import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { Link } from "../../i18n/navigation";

export default function HomePage({ params }: PageProps<"/[locale]">) {
  const { locale } = use(params);
  setRequestLocale(locale);
  const t = useTranslations("Home");

  return (
    <main>
      <h1>{t("title")}</h1>
      <p>{t("description")}</p>

      <Link href="/login">Login</Link>
    </main>
  );
}
