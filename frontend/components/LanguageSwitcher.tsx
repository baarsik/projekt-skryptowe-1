"use client";

import { useLocale } from "next-intl";
import {
  usePathname,
  useRouter,
} from "../i18n/navigation";
import { useTransition } from "react";

export default function LanguageSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();

  const [isPending, startTransition] = useTransition();

  function handleLanguageChange(
    event: React.ChangeEvent<HTMLSelectElement>
  ) {
    const nextLocale = event.target.value;

    startTransition(() => {
      router.replace(pathname, {
        locale: nextLocale,
      });
    });
  }

  return (
    <select
      value={locale}
      onChange={handleLanguageChange}
      disabled={isPending}
      aria-label="Select language"
    >
      <option value="en">English</option>
      <option value="pl">Polski</option>
    </select>
  );
}