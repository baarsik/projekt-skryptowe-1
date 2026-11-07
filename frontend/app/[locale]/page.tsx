
import { useTranslations } from "next-intl";
import { Link } from "../../i18n/navigation";

export default function HomePage() {
  const t = useTranslations("Home");

  return (
    <main>
      <h1>{t("title")}</h1>
      <p>{t("description")}</p>

      <Link href="/login">Login</Link>
    </main>
  );
}
