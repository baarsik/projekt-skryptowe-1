import Link from "next/link";
import { routing } from "../../i18n/routing";

export default function RootPage() {
  return <Link href={`/${routing.defaultLocale}/`}>Przejdź do aplikacji</Link>;
}
